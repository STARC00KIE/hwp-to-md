import win32com.client as win32
import os

def hwp_to_pdf(
        INPUT_FOLDER="./docs/hwp",
        OUTPUT_FOLDER="./docs/pdf",
        PRINTER_NAME="Microsoft Print to PDF", 
        PRINT_METHOD=0,
        ) -> None:
    """
    한컴2024 api를 활용하여 PDF로 변환 저장
    :param INPUT_FOLDER: 한글파일들이 저장되어 있는 경로
    :param OUTPUT_FOLER: 변환된 파일들을 저장할 경로
    :PRINTER_NAME: 사용할 프린터 이름(Microsoft Print to PDF, Hancom PDF)
    """

    print(f"변환 시작: '{INPUT_FOLDER}' -> '{OUTPUT_FOLDER}'")
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") #보안 경고 창 없애기(ReadMe 참조)

    hwp_files = os.listdir(INPUT_FOLDER)
    
    for hwp_file in hwp_files:
        # hwp 파일 절대경로
        hwp_path = os.path.join(os.path.abspath(INPUT_FOLDER), hwp_file)
        # 파일명(확장자 제외)만 추출
        file_name_without_ext = os.path.splitext(hwp_file)[0]
        pdf_file_name = f"{file_name_without_ext}.pdf"
        # pdf 파일 절대경로
        pdf_path = os.path.join(os.path.abspath(OUTPUT_FOLDER), pdf_file_name)

        # 파일 열기
        hwp.Open(hwp_path) 

        # pdf 저장을 진행하면 -> 모아찍기 버그 존재
        # pdf로 인쇄로 방법 변경
        act = hwp.CreateAction("Print")
        pset = act.CreateSet()
        act.GetDefault(pset)

        pset.SetItem("PrintMethod", PRINT_METHOD)  # 0:보통출력, 4:2쪽모아찍기 등
        pset.SetItem("FileName", pdf_path)  # 전체경로 포함한 파일이름
        pset.SetItem("PrinterName", PRINTER_NAME)  # "Microsoft Print to PDF" 등

        act.Execute(pset)
        hwp.Run("FileClose")

    hwp.Quit()

if __name__ == "__main__":
    hwp_to_pdf()