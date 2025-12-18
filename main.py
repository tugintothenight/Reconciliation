from docx import Document
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
import Levenshtein
import difflib
from colorama import Fore, Style, init
nltk.download("punkt")
init(autoreset=True)
RUN_TEST_MODE = True


def extract_text_paddleocr(pdf_path):
    pages = convert_from_path(pdf_path)
    ocr = PaddleOCR(lang='en', use_textline_orientation=True)
    all_text = []
    for idx, page in enumerate(pages):
        img_path = f"page_{idx}.jpg"
        page.save(img_path, "JPEG")
        result = ocr.predict(img_path)
        if not result or not isinstance(result, list):
            continue
        data = result[0]
        texts = data.get("rec_texts", [])
        for text in texts:
            all_text.append(text)
    return "\n".join(all_text)


def extract_text_from_docx(path):
    doc = Document(path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)


pdf_text = extract_text_paddleocr("ds.pdf")
doc_text = extract_text_from_docx("ds.docx")
doc_chunk = sent_tokenize(doc_text)
pdf_chunk = sent_tokenize(pdf_text)
print('doc: ', doc_text)
print('pdf: ', pdf_text)

print(doc_chunk, pdf_chunk)


tokenized_doc = [word_tokenize(chunk.lower()) for chunk in doc_chunk]
tokenized_pdf = [word_tokenize(chunk.lower()) for chunk in pdf_chunk]

bm25 = BM25Okapi(tokenized_pdf)


# KEYWORD MATCHING
def bm25_best_match(query_chunk):
    query_tokens = word_tokenize(query_chunk.lower())
    scores = bm25.get_scores(query_tokens)
    best_id = scores.argmax()
    return best_id, scores[best_id]


bm25_matches = []
for i, chunk in enumerate(doc_chunk):
    pid, score = bm25_best_match(chunk)
    bm25_matches.append((i, pid, score))
    print(f"BM25 match DOC[{i}] → PDF[{pid}] | score={score}")


# SEMANTIC MATCHING
model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(doc_chunk, convert_to_tensor=True)
pdf_emb = model.encode(pdf_chunk, convert_to_tensor=True)

semantic_scores = util.cos_sim(doc_emb, pdf_emb)

for i in range(len(doc_chunk)):
    best_pdf = semantic_scores[i].argmax().item()
    sim = semantic_scores[i][best_pdf].item()
    print(f"Embedding match DOC[{i}] → PDF[{best_pdf}] | sim={sim:.4f}")


# LEVENSHTEIN CHARACTER DISTANCE
def character_diff(a, b):
    dist = Levenshtein.distance(a, b)
    max_len = max(len(a), len(b))
    diff_ratio = dist / max_len
    return dist, diff_ratio


def print_diff_console(doc_text, pdf_text):
    matcher = difflib.SequenceMatcher(None, doc_text, doc_text)
    matcher.set_seq2(pdf_text)
    output_parts = []
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == 'equal':
            output_parts.append(doc_text[i1:i2])
        elif opcode == 'replace':
            output_parts.append(f"{Fore.RED}{doc_text[i1:i2]}{Style.RESET_ALL}")
            output_parts.append(f"{Fore.GREEN}{pdf_text[j1:j2]}{Style.RESET_ALL}")
        elif opcode == 'delete':
            output_parts.append(f"{Fore.RED}{doc_text[i1:i2]}{Style.RESET_ALL}")
        elif opcode == 'insert':
            output_parts.append(f"{Fore.GREEN}{pdf_text[j1:j2]}{Style.RESET_ALL}")

    print("".join(output_parts))


for i, chunk in enumerate(doc_chunk):
    pdf_id = semantic_scores[i].argmax().item()
    dist, ratio = character_diff(chunk, pdf_chunk[pdf_id])
    print(f"Levenshtein DOC[{i}] vs PDF[{pdf_id}] → dist={dist}, ratio={ratio:.3f}")

final_results = []

for doc_id, bm25_pdf, bm25_score in bm25_matches:
    embed_pdf = semantic_scores[doc_id].argmax().item()
    embed_score = semantic_scores[doc_id][embed_pdf].item()
    dist, ratio = character_diff(doc_chunk[doc_id], pdf_chunk[embed_pdf])

    final_results.append({
        "doc_id": doc_id,
        "pdf_id giống keyword nhất": bm25_pdf,
        "bm25 score": bm25_score,
        "pdf_id giống nghĩa nhất": embed_pdf,
        "embed score": embed_score,
        "số kí tự khác": dist,
        "tỉ lệ khác": ratio
    })

print("\nFINAL RESULTS:")
for item in final_results:
    print(item)

print('So sánh kí tự: (đỏ là doc, xanh là pdf, trắng là phần giống)')
for i, (doc_sent, pdf_sent) in enumerate(zip(doc_chunk, pdf_chunk)):
    print(f"\n[Câu {i+1}]:")
    print_diff_console(doc_sent, pdf_sent)