# Yunseo-Lab 프로필 유지보수

이 저장소는 GitHub 계정 `Yunseo-Lab`의 Overview에 표시되는 프로필이다. 사용자가 승인한 리포 분류와 NUBI 디자인을 유지하면서, 실제 계정의 저장소 목록·설명·링크를 정확하게 반영한다. 사용자의 명시적인 최신 지시가 이 문서보다 우선한다.

이 지침은 **이 저장소에서 작업하는 에이전트**에게 적용된다. 다른 프로젝트에서 새 리포를 만들 때에는 이 문서를 직접 읽고 같은 규칙을 적용한 뒤, 이 프로필 저장소도 갱신한다. 이 파일만으로 다른 저장소에 지침이 자동 적용되지는 않는다. Codex의 적용 범위는 [공식 AGENTS.md 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)를 참고한다.

## 1. 저장소 이름과 분류

| 공개 여부 / 분류 | 이름 규칙 | 기준 |
| --- | --- | --- |
| Public work | 비공개용 prefix 없음 | 공개 프로젝트, 공개 도구, 공개 참고용 fork 모두 포함 |
| Projects | `proj-<name>` | 앱·서비스·게임 등 결과물을 만드는 프로젝트 |
| Labs | `lab-<name>` | 구현하며 탐구하는 실험·검증·재현·프로토타입 |
| Study | `study-<name>` | 교재·수업·이론을 따라 정리하는 학습 기록 |
| Tools | `tool-<name>` | 실제로 반복 사용하며 작업을 줄이는 자동화·유틸리티 |
| Space | `space-<name>` | 세컨드 브레인·블로그·포트폴리오를 담는 개인 공간 |

- **공개 리포에는 위 비공개 prefix를 붙이지 않는다. 비공개 리포에만 붙인다.** 공개 리포가 프로젝트여도 프로필의 Public work에 표시한다.
- 새 일반 비공개 이름은 소문자 kebab-case로 쓴다. 기존 공개 리포의 고유 표기와 fork 이름은 보존한다.
- 실습·구현이 중심이면 보통 `proj-` 또는 `lab-`, 문서 기록이 중심이면 `study-` 또는 `space-`다. 단순히 코드가 있다는 이유로 승인된 기존 분류를 바꾸지 않는다.
- `lab-hello-agent`, `lab-embedding-classification`, `lab-langchain-mcp`, `lab-ref-ranker`는 실험이다. `proj-game`, `proj-chat-frontend`, `proj-storybook-studio`, `proj-llm-chat-app`은 프로젝트다. `tool-auto-video-downloader`는 도구의 기준 사례다.
- `Yunseo-Lab.github.io`는 이름 변경 금지 예외다. 현재 목록에 없더라도 임의로 만들거나 복원하지 않는다. 다시 나타나면 실제 공개 여부와 의도를 확인하고, 비공개라면 승인된 `category_override`로 원래 이름을 유지한다.
- 프로필 동기화를 이유로 원격 리포 이름·공개 여부·보관 상태를 임의로 바꾸지 않는다. 그런 변경은 사용자가 요청한 작업 범위에서만 수행한다. 동기화 스크립트는 원격 설정을 변경하지 않는다.

## 2. 내용과 공개 범위

- 소유 계정의 모든 리포를 포함한다. 공개 fork도 포함한다. 별도 계정·조직이 소유한 협업 리포는 자동 수집 대상이 아니다.
- 사용자는 **비공개 리포의 이름과 설명을 공개 프로필에 나열하는 것**을 승인했다. 링크는 원래 리포로 연결하고, 접근 권한은 GitHub에서 그대로 유지한다. 비공개 코드·문서 본문·토큰을 가져오거나 공개하지 않는다.
- 모든 리포에는 실제 용도를 설명하는 간결하고 정확한 GitHub description이 있어야 한다. 이름만 보고 기능이나 본인 기여를 지어내지 말고, 필요하면 해당 리포 README와 내용을 확인한다. 공개 fork의 원저자 성과를 본인 작업처럼 쓰지 않는다.
- `data/repositories.json`의 `description`은 실제 GitHub description이다. `description_override`는 승인된 카드용 문구다. 원격 설명이 바뀌면 override도 검토한다. 새 override는 불필요하게 추가하지 않는다.
- 설명을 말줄임표로 자르지 않는다. 긴 문장은 줄바꿈과 카드 높이로 수용한다. 원래 전체 설명은 이미지 대체 텍스트와 SVG 메타데이터에도 남긴다.
- 기존 영문 소개와 공개 리포 설명, 한국어 비공개 리포 설명을 유지한다. 일괄 번역이나 기능 추정은 하지 않는다.
- `Selected work`는 다시 넣지 않는다. 리포를 숨긴 축약 목록이나 `View all` 대신 모든 카드를 펼쳐 보여 준다.

## 3. 파일 구조와 편집 위치

```text
data/
  profile.json             # 소개, 배너, 카테고리, 순서, 우선 노출할 리포 ID
  repositories.json        # GitHub 메타데이터 + 승인된 문구/그림 연결
assets/
  branding/                # 현재 사용하는 메인 배너
  illustrations/categories/# 여섯 분류의 NUBI 그림 (탐색 메뉴와 기본 카드 공용)
  illustrations/cards/     # 개별 리포에 연결한 NUBI 그림
  fonts/                   # 재생성용 원본 글꼴과 OFL 라이선스
  generated/cards/         # 자동 생성: 리포별 desktop/mobile SVG
  generated/sections/      # 자동 생성: 분류별 desktop/mobile SVG
scripts/
  sync_repositories.py     # GitHub → 로컬 목록 비교/갱신
  profile_data.py          # 분류, 정렬, 입력 검증
  build_profile.py         # 데이터 → README와 SVG 생성
  check_profile.py         # 링크, 개수, SVG, 에셋 참조 검증
tests/                     # 이름/공개 여부 변경과 동기화 회귀 검사
README.md                  # 자동 생성된 GitHub 프로필
```

`README.md`와 `assets/generated/`를 수동으로 고치지 않는다. 내용은 `data/`, 표현은 생성 스크립트를 수정하고 재생성한다. 생성 결과도 커밋한다. 외부 CDN 서비스나 개발자의 절대 경로 없이 이 저장소만으로 다시 만들 수 있어야 한다.

리포는 이름이 아닌 **GitHub의 고유 ID**로 연결한다. 이름 변경 시 기존 그림·override·우선순위를 유지한다. `preferred_ids`에 없는 새 리포는 해당 분류의 이름순으로 표시한다. Public work는 자체 리포를 먼저, fork를 뒤에 둔다. 기존 우선 노출 순서를 임의로 재배치하지 않는다.

## 4. 새 리포 또는 변경 사항 반영 절차

프로젝트를 새로 게시했거나 이름·설명·공개 여부를 바꿨다면 이 저장소까지 함께 갱신한다. 날짜나 리포 개수는 하드코딩하지 않는다.

초기 환경 준비(Python 3.11 이상, GitHub CLI 필요):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

작업 순서:

1. `git status`와 원격 최신 상태를 확인한다. 사용자 변경을 덮어쓰지 않는다. `gh`는 비공개 리포를 읽을 수 있는 `Yunseo-Lab` 계정이어야 한다.
2. 먼저 읽기 전용으로 비교한다. 변경이 있으면 종료 코드 1, API·입력 오류는 2다.

   ```sh
   .venv/bin/python scripts/sync_repositories.py --check
   ```

3. 실제 리포 이름·분류·설명을 검토한다. description 누락이나 규칙에 맞지 않는 이름은 추측으로 덮지 않는다. 사용자 요청 범위에서 실제 리포를 정리하거나 필요한 판단을 확인한다. 로컬 목록에 반영한다.

   ```sh
   .venv/bin/python scripts/sync_repositories.py --apply
   ```

4. `data/repositories.json` diff를 확인한다. 새 리포는 분류의 기본 NUBI 그림을 사용한다. 기존 개별 그림과 문구는 유지하고, 설명 변경 시 `REVIEW description_override` 항목을 검토한다. 필요할 때만 개별 그림 또는 우선순위 ID를 조정한다.
5. 생성하고 검증한다.

   ```sh
   .venv/bin/python scripts/build_profile.py
   .venv/bin/python scripts/build_profile.py --check
   .venv/bin/python scripts/check_profile.py
   .venv/bin/python -m unittest discover -s tests
   ```

6. diff에서 원격 링크, 설명, 분류별 개수와 전체 개수, desktop/mobile 결과를 확인한다. 사용자 요청 범위에서 커밋·게시하고 원격 결과를 확인한다. 강제 push는 하지 않는다.

변경별 주의점:

- **새 리포:** 공개 여부 → prefix/분류 → 실제 설명 → 목록 동기화 → 카드 생성 순서다. 새 이미지 생성은 필수가 아니다.
- **이름 변경:** ID는 유지하고 메타데이터를 갱신한다. 새 파일명과 링크는 자동 생성되며 이전 이름의 SVG는 생성기가 제거한다. 같은 리포를 별도 항목으로 추가하지 않는다.
- **설명 변경:** 원격 description과 카드 override를 함께 검토한다. 카드 전체 문장이 보이는지 확인한다.
- **공개/비공개 전환:** 공개 리포의 prefix 제거, 비공개 리포의 적절한 prefix 추가는 해당 변경에 대한 사용자 지시 안에서 처리한다. 이후 목록을 갱신하면 분류와 개수가 다시 계산된다.
- **삭제/계정 이전:** 먼저 권한 부족·다른 로그인·불완전한 응답이 아닌지 확인한다. 스크립트는 누락을 자동 삭제하지 않는다. 실제 삭제/이전이 확인된 경우에만 `--apply --allow-removals`로 **로컬 목록**에서 제거한다. 원격 삭제 명령이 아니다. 필요하면 `preferred_ids`의 사라진 ID도 정리한다.
- **보관 처리:** GitHub에 존재하는 소유 리포라면 목록에 유지한다. archived 상태만으로 숨기지 않는다.
- **프로필 전용 디자인 변경:** 원격 메타데이터 수정은 필요 없다. 원본 설정/생성기를 수정하고 두 화면 크기를 확인한다.

## 5. 승인된 디자인과 GitHub 제약

- 은색 NUBI, 연한 모브 계열, 현재 메인 배너를 유지한다. 배너/캐릭터를 별도 요청 없이 재생성하지 않는다.
- 분류 순서는 `Public work → Projects → Labs → Study → Tools → Space`다. 여섯 스티커 탐색 메뉴, 분류 헤더, 리포별 클릭 가능한 카드 구조를 유지한다.
- 넓은 화면에서는 카드 두 열, 좁은 화면에서는 한 열이다. 카드 폭 410 SVG 좌표계, 섹션 헤더 desktop 840 / mobile 410을 기준으로 하고 `<picture>`로 모바일 변형을 제공한다.
- GitHub README의 임의 CSS·스크립트·flex/grid HTML 레이아웃에 의존하지 않는다. README의 표는 상단 탐색 메뉴에만 사용한다. 카드 디자인은 자기완결형 SVG 이미지 안에 둔다.
- SVG 안의 그림과 subset WOFF2 글꼴은 data URI로 포함한다. 외부 리소스 로딩이 필요 없게 유지한다. Pretendard 원본과 OFL을 보존하고, 수정된 subset의 글꼴 이름은 `NubiCard`로 둔다.
- 생성 SVG의 URL 쿼리는 내용 해시로 자동 갱신된다. 수동 날짜·임의 버전 문자열을 덧붙이지 않는다.
- 리포 이름/설명이 길어져도 잘리지 않게 한다. 폰트 크기·줄바꿈·카드 높이를 바꾸면 실제 GitHub 렌더링에서 이름, 본문, 그림 겹침을 확인한다.
- 레이아웃·글꼴·새 그림을 바꿨을 때는 실제 GitHub 또는 같은 README 렌더러에서 desktop 약 1280px, mobile 약 390px로 검사한다. 이미지 로딩, 두 열/한 열 배치, 긴 이름·설명, 카테고리 이동, 리포 링크 클릭을 확인한다. 단순 메타데이터 변경에는 관련 카드 확인으로 범위를 줄일 수 있다.

## 6. 에셋 정리와 검증

- `check_profile.py`는 직접 표시되는 파일뿐 아니라 데이터에서 참조하는 그림·글꼴·라이선스까지 검사한다. README에 직접 등장하지 않는다는 이유만으로 원본을 지우지 않는다.
- 사용하지 않는 이전 배너, 중복 고해상도 스티커, 이전 생성 결과는 참조가 없음을 확인한 뒤 삭제한다. 필요한 그림은 현재 웹용 PNG 하나를 공유한다. 새 디자인의 편집 원본이 실제로 필요하면 역할을 명확히 구분한다.
- 생성기는 `assets/generated/cards/`와 `assets/generated/sections/`의 불필요한 SVG만 정리한다. 원본 에셋을 자동 삭제하도록 확장하지 않는다.
- `.venv/`, `.cache/`, 스크린샷, 임시 시안, API 원본 덤프, 개인 로컬 경로는 커밋하지 않는다. 배포에 필요한 데이터와 결과물만 포함한다.
- 글꼴·생성 알고리즘·의존성을 바꾼 경우 캐시를 사용하지 않은 재생성도 일치해야 한다.

  ```sh
  .venv/bin/python scripts/build_profile.py --check --no-cache
  ```

- 최종 보고에는 무엇을 정리했는지, 문서/생성 방식이 어떻게 바뀌었는지, 수행한 검증과 원격 반영 여부를 간단히 남긴다.
