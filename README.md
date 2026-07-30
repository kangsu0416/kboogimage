# 번호의 주인: 야구편 OG 이미지

번호의 주인: 야구편의 결과 공유에 사용하는 정적 OG 이미지 저장소입니다.

- 이미지 규격: PNG, 1200 × 600
- 구성: 10개 연고지 × 5개 덕력 등급
- 현재 공개 경로: `https://kangsu0416.github.io/kboogimage/og-results-v3/{teamId}/tier-{tier}.png`
- 이전 브랜드 경로: `https://kangsu0416.github.io/kboogimage/og-results-v2/{teamId}/tier-{tier}.png`
- 기존 경로: `https://kangsu0416.github.io/kboogimage/og-results/{teamId}/tier-{tier}.png`

## Team IDs

- `daegu`
- `seoul-lg`
- `seoul-doosan`
- `suwon`
- `seoul-kiwoom`
- `gwangju`
- `daejeon`
- `changwon`
- `busan`
- `incheon`

## Tiers

- `starter`: 덕력 충전 중
- `bronze`: 야구팬 인증
- `silver`: 열혈 야구팬
- `gold`: 로스터 전문가
- `champion`: 라인업 마스터

`og-results-v3`는 새 헤더 카드와 간격 규칙을 적용한 현재 버전이다. 기존 공유 링크의 호환성을 위해 `og-results`와 `og-results-v2`를 보존한다. `og-results-v2`도 같은 최신 이미지로 갱신하지만, 새로 생성되는 공유 링크는 캐시 무효화를 위해 `og-results-v3`를 사용한다.

## OG 이미지 생성 규칙

- 생성 원본은 `og-results`이고, `tools/rebrand_og_images.py`로 `og-results-v2`와 `og-results-v3`를 함께 만든다.
- AI 원본에 포함된 브랜드·연고지 글자는 그대로 사용하지 않는다. 오른쪽 상단을 불투명 헤더 카드로 덮고 브랜드명과 연고지를 프로그램으로 다시 조판한다.
- 브랜드명은 정확히 `번호의 주인: 야구편`으로 표기한다.
- 브랜드명은 28~30px Bold, 연고지는 48~68px Arial Black 범위에서 카드 내부 최대 폭 360px에 맞춰 자동 축소한다.
- 브랜드명 glyph 하단과 연고지 glyph 상단은 최소 40px을 확보한다. 디자인 최소 허용값은 32px이지만 생성기는 압축·그림자 오차를 고려해 40px 미만을 실패 처리한다.
- 연고지에는 사용자가 확정한 팀 메인 컬러를 적용한다. 수원은 검정, 잠실(엘)은 레드, 잠실(두)은 네이비를 사용한다.
- 브랜드명 glyph 하단과 연고지 glyph 상단은 40px 이상, 생성 결과의 목표값은 55px으로 고정한다.
- 헤더 카드 박스 하단과 덕력 등급 glyph 상단은 최소 32px, 헤더 그림자의 광학 경계와 등급명 사이는 최소 20px 이상을 확보한다.
- 구 브랜드·연고지·밑줄이 새 카드 밖에 남아 있으면 생성 결과를 사용하지 않는다.
- 캔버스 바깥 안전영역은 좌우 72px, 상하 54px을 기준으로 한다.
- 결과 파일은 PNG, 1200×600, RGB여야 하며 10개 연고지 × 5개 등급의 총 50장이 모두 있어야 한다.

생성:

```powershell
python tools/rebrand_og_images.py
```

검증:

```powershell
python tools/validate_og_images.py
```
