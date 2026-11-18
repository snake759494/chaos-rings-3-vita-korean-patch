# 재빌드 방법

필요한 것: Python 3.11 이상, Pillow, NumPy, fontTools, 원본 게임 파일, [글꼴](FONT_CREDITS.md).

1. 복호화된 게임 폴더의 `CR3/resources/`에서 원본 파일을 `work/base/`에 복사합니다. 해시는 `release_manifest.json`과 같아야 합니다.
   - `CRDB.psp2.mvgl`, `CRDBboot.psp2.mvgl`, `CRDBui01.psp2.mvgl`, `CRDBadv01.psp2.mvgl`, `CRDBbundle.psp2.mvgl`, `CRDBcardhd.psp2.mvgl`
   - `font/TBGB_0KP.TTC`(`work/base/TBGB_0KP.TTC`로 복사)
2. 대사 묶음을 풀고 원문 목록을 만듭니다.
   ```powershell
   cd tools
   python extract.py ..\work\base\CRDB.psp2.mvgl ..\work\crdb
   python extract_all.py
   ```
   `work/tr/index.json`(원문 목록)이 생깁니다. 번호는 `text/tr/`의 번호와 같습니다.
3. 번역과 그림 글자 정의를 작업 폴더에 둡니다.
   ```powershell
   New-Item -ItemType Directory -Force ..\work\tr\out, ..\work\img
   Copy-Item ..\text\tr\*.txt ..\work\tr\out\
   Copy-Item ..\text\images\*.json ..\work\img\
   ```
4. 빌드합니다. 결과는 `out/`에 생깁니다.
   ```powershell
   python build.py
   ```
5. 번역을 검증하려면 `python check_tr.py`를 실행합니다. 제어 코드·변수·줄 수가 원문과 맞는지 검사합니다.

## 주의

- 일부 그림(약 120장)은 손으로 다듬은 한글 텍스처(`work/imgdata/`)를 바탕으로 만들었습니다. 그 텍스처는 게임 그림에서 파생된 것이라 저장소에 넣지 않았습니다. 그래서 저장소만으로 빌드하면 이 그림들은 원본 그대로 남고, 결과 해시가 릴리즈와 달라집니다. 완성본은 릴리즈의 xdelta를 쓰세요.
- 그림 글자 정의 형식은 `tools/imgpatch.py` 맨 앞의 설명을 참고하세요.
