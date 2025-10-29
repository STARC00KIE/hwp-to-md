# 파일 이름: vllm_automation.p
import os
import subprocess
from tqdm import tqdm

# --- 설정 ---
INPUT_DIRECTORY = "../../../docs/pdf"
# [수정됨] 결과를 저장할 폴더를 더 명확하게 지정 (예: md 폴더)
OUTPUT_MD_DIRECTORY = "../../../docs/md" 
WORKER_SCRIPT = "run_dpsk_ocr_pdf.py"
# --- 설정 끝 ---

def main():
    if not os.path.isdir(INPUT_DIRECTORY):
        print(f"오류: 입력 폴더 '{INPUT_DIRECTORY}'를 찾을 수 없습니다.")
        return
    
    # [수정됨] 출력 폴더를 미리 생성
    os.makedirs(OUTPUT_MD_DIRECTORY, exist_ok=True)

    pdf_files = [f for f in sorted(os.listdir(INPUT_DIRECTORY)) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"'{INPUT_DIRECTORY}' 폴더에서 PDF 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(pdf_files)}개의 PDF 파일을 처리합니다.")

    for pdf_filename in tqdm(pdf_files, desc="전체 진행률"):
        
        # [수정됨] 각 파일에 대한 새로운 출력 경로 변수 생성
        # 1. 파일 이름에서 확장자(.pdf)를 제거
        base_filename = os.path.splitext(pdf_filename)[0]
        # 2. 새로운 확장자(.md)를 붙여 저장할 출력 폴더 이름
        output_md_filename = f"{base_filename}"
        # 3. 기본 출력 폴더와 합쳐 전체 출력 파일 경로를 완성
        output_file_path = os.path.join(OUTPUT_MD_DIRECTORY, output_md_filename)
        
        input_file_path = os.path.join(INPUT_DIRECTORY, pdf_filename)
        
        print(f"\n▶ 처리 시작: {pdf_filename}")
        
        command = [
            "python",
            WORKER_SCRIPT,
            "--input_path",
            input_file_path,
            "--output_path",
            output_file_path  # 새로 만든 출력 파일 경로를 전달
        ]
        
        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, encoding='utf-8'
            )
            print(f"처리 성공: {pdf_filename} -> {output_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"처리 실패: {pdf_filename}")
            print(f"  - 에러 코드: {e.returncode}")
            print("  - 에러 메시지 (STDERR):")
            for line in e.stderr.strip().split('\n'):
                print(f"    {line}")

if __name__ == "__main__":
    main()