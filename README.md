# 카오스링 III PS Vita 한글패치

PS Vita 일본판 **카오스링 III(ケイオスリングスIII, PCSG00500)**용 비공식 한국어 패치입니다. 스토리 대사, 메뉴·시스템 메시지, 아이템·장비·스킬·진(Gene) 설명, 퀘스트·상점·도감 등 게임 안 일본어 문자열 **24,378개 전체**를 직접 한국어로 옮겼습니다. 게임 글꼴에 한글 **2,354자**를 넣었습니다. 타이틀 로고 아래에는 한글 부제를 넣었습니다. 메뉴·버튼·튜토리얼 화면·배틀/이벤트 배너 등 그림 글자도 한글로 다시 그렸습니다. 현재 배포판은 **v1.0.1 (2026-11-18)**입니다.

[패치 다운로드](https://github.com/snake759494/chaos-rings-3-vita-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [용어집](docs/GLOSSARY.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 게임 데이터 파일 7개에 각각 대응하는 xdelta 7개입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 다음 파일은 포함하지 않습니다.

- 원본·완성 게임 파일
- 추출한 게임 데이터·그림
- 일본어 원문
- 글꼴 파일
- 외부 실행 파일

GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『카오스링 III』는 스퀘어 에닉스가 내고 Media.Vision이 개발한 『카오스링』 시리즈 3편 RPG입니다. 스마트폰판에 이어 PS Vita판이 일본에서 나왔습니다.

이 패치는 **PS Vita 일본판(PCSG00500)**의 `CR3/resources/` 폴더에 있는 파일 7개에 적용합니다. 복호화된 게임 폴더(`ux0:app/PCSG00500/`)에 있는 파일이어야 합니다. 파일 이름보다 아래 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| xdelta | 대상 파일(`CR3/resources/` 기준) | 원본 크기 | 원본 MD5 |
| --- | --- | --- | --- |
| `..._text.xdelta` | `CRDB.psp2.mvgl` (대사·메뉴·데이터 문장) | 13,329,361 B | `fbc5f915649541501d15ffe0c4576581` |
| `..._boot.xdelta` | `CRDBboot.psp2.mvgl` (시스템 메시지·타이틀·공용 UI 그림) | 26,093,571 B | `120c493a03e7d9ec4a74ee7e8ab0bf9c` |
| `..._ui.xdelta` | `CRDBui01.psp2.mvgl` (메뉴·튜토리얼·배너 그림) | 136,205,691 B | `453436ec79991dacceb32c7fe2d709ad` |
| `..._adv.xdelta` | `CRDBadv01.psp2.mvgl` (이벤트 화면 그림) | 4,968,084 B | `e17c0c493d0ed4c0cd984b17d934de6b` |
| `..._bundle.xdelta` | `CRDBbundle.psp2.mvgl` (공용 그림) | 136,962 B | `c1746fc6edbb531e01ea0decc3a1c5fb` |
| `..._cardhd.xdelta` | `CRDBcardhd.psp2.mvgl` (카드 뷰어 버튼) | 90,387,380 B | `222ffb089265bd8954bd914b38f83e56` |
| `..._font.xdelta` | `font/TBGB_0KP.TTC` (게임 글꼴) | 2,658,164 B | `f66352dc554df64ad2467fdb68aa9a6e` |

결과 파일과 xdelta 자체의 크기·MD5·SHA-1·SHA-256은 [release_manifest.json](release_manifest.json)과 릴리즈 설명에 있습니다. 원본 게임 파일은 사용자가 직접 준비해야 합니다. `eboot.bin`과 그 밖의 파일은 바꾸지 않습니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\CRDB.psp2.mvgl'
```

나머지 파일도 같은 방법으로 확인합니다. 위 표와 다르면 적용을 중단하세요.

### xdelta UI 사용

1. 릴리즈에서 xdelta 7개를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. 파일마다 **Patch**에는 xdelta 파일을 선택합니다. **Source File**에는 위 표에서 짝이 되는 원본 파일을 선택합니다(`..._text.xdelta` → `CRDB.psp2.mvgl`).
4. **Output File**에는 새 파일 이름을 지정합니다. 7개를 모두 만든 뒤 원래 이름으로 바꿔 아래 위치에 넣습니다.

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. 그래서 적용이 빠릅니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\CRDB.psp2.mvgl' '.\Chaos_Rings_III_Vita_KO_v1.0.1_text.xdelta' '.\ko\CRDB.psp2.mvgl'
```

나머지 6개도 같은 방식입니다. 해시를 자동으로 검사하는 도구도 있습니다. Python 3와 xdelta3가 필요합니다. `--source-dir`에는 원본 `resources` 폴더를, `--patch-dir`에는 xdelta 7개가 있는 폴더를 지정합니다. 결과는 출력 폴더에 같은 구조(`font/` 포함)로 만들어집니다. 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source-dir '.\resources' --patch-dir '.\patch' --output-dir '.\ko'
```

### 게임에 넣기

- **PS Vita 실기(rePatch, 권장)**: 결과 파일을 `ux0:rePatch/PCSG00500/CR3/resources/`에 복사합니다. 글꼴은 `font/TBGB_0KP.TTC`에 넣습니다. 원본 게임 폴더는 그대로 둡니다.
- **PS Vita 실기(직접 교체)**: `ux0:app/PCSG00500/CR3/resources/`의 원본 7개를 백업한 뒤 결과 파일로 덮어씁니다.
- **Vita3K**: 설치된 게임 폴더(`<Vita3K 데이터 폴더>/ux0/app/PCSG00500/CR3/resources/`)의 원본 7개를 결과 파일로 바꿉니다.

7개를 모두 바꿔야 합니다. 일본판이므로 **○ 버튼이 결정, ✕ 버튼이 취소**입니다. 세이브 데이터 형식은 바꾸지 않았습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 스토리 | 메인 시나리오·서브 이벤트·동료 대화·퀘스트 대사 |
| 메뉴·시스템 | 타이틀·세이브/로드·캠프 메뉴·설정·확인창·튜토리얼 문장·배틀 커맨드·결과 화면 |
| 데이터 | 아이템·장비·액세서리·진·스킬·적 이름과 설명, 상점·퀘스트·도감 |
| 문장 | 일본어 문자열 **24,378개 전체**(대화 메시지, MBE 표, BSON 데이터, 스크립트 문자열) |
| 게임 글꼴 | `TBGB_0KP.TTC`의 두 글꼴에 한글 **2,354자** 추가(나눔스퀘어네오 Bd) |
| 그림 글자 | 타이틀 한글 부제, 세이브·전투·메뉴·상점·파티 교체 등 UI 그림 글자, 튜토리얼 스크린샷 속 라벨, 배틀 모드·이벤트 배너, 무비 일시정지/스킵 버튼, 경고 화면, 카드 뷰어 닫기 버튼 |

바꾼 데이터는 MDB1(`.mvgl`) 묶음을 다시 만들어 넣었습니다. 대사 문자열은 원본 길이 제한 없이 새로 배치합니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 일본어 원문과 문맥을 보며 직접 번역했습니다.
- 인물·지명·게임 용어는 [용어집](docs/GLOSSARY.md)대로 통일했습니다. 예: 리어리, 다이스케, 에루루, 진, 익스플로러, 꿈의 세계수.
- 대사창 폭에 맞춰 원문과 같은 줄 수를 유지했습니다. 캐릭터 말투(반말·존댓말·어린아이 말투)를 살렸습니다. 시스템 문구는 「~합니다/~하시겠습니까?」로 통일했습니다.

### 번역하지 않은 것

- 음성(일본어)
- 스태프롤, 저작권 표기
- 작품 로고(타이틀 로고 아래에 한글 부제만 추가)
- 일부 튜토리얼 스크린샷 속 아주 작은 글씨나 반사된 글씨
- 온라인 기능(서비스 종료)

## 알려진 한계

- 모든 장면을 게임에서 직접 플레이하며 확인하지는 못했습니다. Vita3K에서 다음 화면을 확인했습니다.
  - 타이틀, 세이브/로드, 프롤로그 대사
  - 튜토리얼, 배틀 커맨드·적 이름·전투 결과
  - 세이브 확인창
- 메뉴·상점·마을 화면은 문자열과 그림 단위로만 점검했고 실제 플레이로는 확인하지 못했습니다.
- 스크립트 파일(`.nut`) 안의 문자열 4개는 아직 바꾸지 않았습니다. 던전 수집 수 표시 등이 해당합니다.
- 글이 상자 밖으로 넘치는 곳이 있으면 이슈로 알려 주세요.
- 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/build.py` | 원본 파일에서 한글판을 빌드(텍스트 교체, 글꼴 병합, 그림 글자 재작성, MDB1 재구성) |
| `tools/` | 빌드·검증 도구(Python) |
| `text/tr/bNNN.txt` | 번역(`번호<TAB>한국어`) |
| `text/images/spec_*.json` | 그림 글자 번역 |
| `docs/` | 기술 설명, 재빌드 방법, 용어집, 글꼴 출처 |

`tools/`의 주요 도구는 다음과 같습니다.

- `mvgl.py`·`repack.py`: MDB1 읽기·재구성
- `msg.py`: 메시지
- `mbe.py`: MBE 표
- `bsonpatch.py`: BSON 문자열 참조
- `gxt.py`: GXT 텍스처
- `fontbuild.py`: TTC 글꼴 병합
- `imgpatch.py`: 그림 글자
- `extract.py`·`extract_all.py`: 원문 목록 생성
- `check_tr.py`: 번역 검증
- `emu.py`: 에뮬레이터 조작
- `apply_release.py`: 해시 검사 후 적용

`text/tr/`의 번호는 `tools/extract_all.py`가 사용자의 원본 파일에서 만드는 원문 목록 순서입니다. `text/images/`의 각 항목에는 텍스처 위치·상자 좌표와 한국어만 들어 있습니다.

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
