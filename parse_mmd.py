import re
import os

def get_folder_name(folder_path):
    folder_names = []

    for name in os.listdir(folder_path):  # 폴더 내의 모든 항목 반복
        full_path = os.path.join(folder_path, name)  # 전체 경로 생성
    
        if os.path.isdir(full_path):  # 해당 항목이 폴더인지 확인
            folder_names.append(name)  # 폴더라면 리스트에 추가

    return folder_names

# 공고명과 사업명 파싱하는 함수 생성
def parse_mmd_info(file_path):

    metadata = {
        "proj_name": None,
        "ann_date": None
    }

    # 파일 열기
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 첫 페이지만 파싱 진행(공고명과 사업명 둘 다 존재)
    # deepseekOCR은 페이지를 "<--- Page Split --->"으로 구분함
    first_page_content = content.split("<--- Page Split --->")[0]

    "======================================================================================"
    # 1. 사업명 추출
    # 첫 페이지에 `사 업 명` 문자 다음에 존재하지만 문자 없이 바로 존재하는 경우(엣지케이스) 존재
    # 나중에 search 진행할 때 속도가 빨라짐 -> 정규표현식 컴파일
    """
    # 정규표현식 해석
    `<td>`: `<td>` 문자열을 그대로 찾음 (HTML 표의 셀 시작 태그)
    `\s*`: 공백(스페이스, 탭, 줄바꿈 등)이 0개 이상 있을 수 있음
    `사\s*업\s*명`: ‘사업명’이라는 한글 단어, 글자 사이에 공백이 있어도 인식 (`사   업  명` 등)
    `</td>`: 첫 번째 셀 닫힘 태그
    `\s*<td>`: 다음 셀 `<td>`로 넘어가는 부분 (공백 허용)
    `(.*?)`: **캡처 그룹** — 실제 우리가 가져오려는 “사업명 내용”을 여기서 뽑음, `?` 는 *non-greedy* 모드라서 가능한 짧게 매칭 |                                                  |
    `</td>`:셀 닫는 태그 — 캡처 끝 위치
    """
    # re.DOTALL 줄바꿈이 들어간 HTML도 포함해서 매칭하게 할 수 있도록 하는 코드
    proj_name_pattern = re.compile(r'<td>\s*사\s*업\s*명\s*</td>\s*<td>(.*?)</td>', re.DOTALL)
    proj_match = proj_name_pattern.search(first_page_content)

    if proj_match:
        raw = proj_match.group(1)
        # <br>, <br/>, <br /> 제거 → 공백으로 치환 후 공백 정리
        cleaned = re.sub(r'<br\s*/?>', ' ', raw, flags=re.I)
        metadata['proj_name'] = re.sub(r'\s+', ' ', cleaned).strip()
    else: # '사업명' 단어 없이 바로 사업명이 나올 때, 문서 상단의 첫 의미 있는 줄을 제목으로 간주
        lines = first_page_content.strip().split('\n')
        
        for line in lines[:5]:
            cleaned_line = line.strip().lstrip('#').strip()
            # 너무 짧으면 이상하므로 제일 앞, 어느정도 길이가 긴 글자를 사업명으로 간주함
            if len(cleaned_line) > 10:
                metadata['proj_name'] = cleaned_line
                break

    "======================================================================================"
    # 2. 공고년월 추출
    date_pattern = re.compile(r'(\d{4})\s*[\.년]\s*(\d{1,2})\s*[\.월]?')
    date_match = date_pattern.search(first_page_content)

    if date_match:
        year = date_match.group(1)
        month = date_match.group(2).zfill(2) # 월은 두자리 고정
        metadata['ann_date'] = f'{year}년 {month}월'

    return metadata

def rename_objects(base_folder_path, old_files, folder_path, new_prefix):
    folder = os.path.basename(os.path.normpath(folder_path))
    safe_prefix = re.sub(r'[\\/:*?"<>|]', '_', new_prefix)

    # 파일명 변경
    for _, suffix in old_files.items():
        old_name = folder + suffix
        old_path = os.path.join(folder_path, old_name)
        if not os.path.exists(old_path):
            continue  # 실제 없는 항목은 조용히 스킵

        new_name = safe_prefix + suffix
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)

    # 폴더명 변경
    old_folder = folder_path
    base_new_folder = os.path.join(base_folder_path, safe_prefix)
    new_folder = base_new_folder

    # 같은 경로면 스킵
    if os.path.abspath(old_folder) != os.path.abspath(new_folder):
        # 이미 존재하면 _01, _02 ... 붙여서 비어있는 폴더명 찾기
        if os.path.exists(new_folder):
            i = 1
            while True:
                cand = os.path.join(base_folder_path, f"{safe_prefix}_{i:02d}")
                if not os.path.exists(cand):
                    new_folder = cand
                    break
                i += 1

        os.rename(old_folder, new_folder)
    
if __name__ == "__main__":
    """
    대표 케이스 2개
    ./docs/md/(제안요청서) 240722 2024년 어르신 건강관리사업 모바일 보건소시스템 UI_UX 기능개선 1부(조달청 의견 반영)_최종/(제안요청서) 240722 2024년 어르신 건강관리사업 모바일 보건소시스템 UI_UX 기능개선 1부(조달청 의견 반영)_최종.mmd
    ./docs/md/CP_20160908812-00_1473654308090_제안요청서(최종)/CP_20160908812-00_1473654308090_제안요청서(최종).mmd
    """
    base_folder_path = './docs/md'
    folders = get_folder_name(base_folder_path)
    for folder in folders:
        # 경로
        folder_path = os.path.join(base_folder_path, folder)

        # 기본 가정: 폴더명과 같은 .mmd
        file_name = folder + '.mmd'
        file_path = os.path.join(folder_path, file_name)

        # 최소 보정: 같은 이름의 .mmd가 없으면, 폴더 안에서 아무 .mmd 나 하나 선택
        if not os.path.exists(file_path):
            mmds = [fn for fn in os.listdir(folder_path) if fn.lower().endswith('.mmd')]
            if len(mmds) == 0:
                print(f"{folder} → .mmd 파일 없음, 스킵\n")
                continue
            # (최소 변경) 가장 긴 파일명 사용: 보통 본문 mmd가 가장 깁니다
            mmds.sort(key=len, reverse=True)
            file_name = mmds[0]
            file_path = os.path.join(folder_path, file_name)

        meta_data = parse_mmd_info(file_path)

        # 기존 파일들 이름 형식
        old_files = {
            "det": "_det.mmd",
            "layout": "_layouts.pdf",
            "main": ".mmd"
        }
        # 바꿀 파일 형식
        base_prefix = f"{meta_data['proj_name']}_{meta_data['ann_date']}"

        # 메타데이터가 None이 아닐 때만 함수 실행
        if None in meta_data.values():
            print(f"⚠️ {folder} → 메타데이터 불완전, 스킵\n")
            continue    
        
        # 바꿀 파일 형식
        rename_objects(base_folder_path, old_files, folder_path, base_prefix)