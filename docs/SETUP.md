# Setup / 상태

1. Python 3.11+; pip install -r requirements.txt
2. Google Cloud Sheets API 활성화, 서비스 계정 생성, 지정 시트 편집 권한 공유.
3. SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON, DELIVERY_API_TOKEN은 환경변수 또는 GitHub Secrets에만 저장. 공개 저장소에 저장 금지.
4. FEEDS_JSON은 허가된 정규화 API의 배열: [{"name":"OKDATA","url":"https://YOUR_AUTHORIZED_ENDPOINT","token_env":"OKDATA_TOKEN","authorized":true}]. 실제 업체별 endpoint, 인증 방식, pagination, 응답 매핑은 계약 및 샘플 응답 확인 후 개발 필요.
5. AUTHORIZED_PAGES_JSON은 허용 확인된 페이지 배열: [{"url":"https://YOUR_AUTHORIZED_PAGE","category_id":"BEAUTY_DEVICE","authorized":true}]. JSON-LD Product만 수집; 타오바오 검색 자동화는 미구현.
6. python -m pytest -q; python pipeline.py; uvicorn api:app --host 127.0.0.1 --port 8000
7. 프론트엔드 서버에서 Bearer 토큰으로 GET /api/v1/references/latest 호출. 토큰을 브라우저에 노출하지 말 것.
8. 배치 실행 권장: 한국시간 00:00 수집 시작, 09:00 이전 배포 목표. 현재 스케줄은 비활성; 실제 연결 확인 후 설정. 단일 실행 워커 사용.

## Normalized feed contract
Array of products: product_id, cluster_id (optional), category_id, title_cn, title_kr, product_url, image_url, price_cny (CNY number), sku_verified (boolean, verified full product), scores (design, price, innovation, marketing, market_response: each 0–100), labels, summary, first_seen_at, listed_at. Upstream must provide real evidence and reviewed scores; do not mark unverified data as verified.

## MVP limitations
Only daily reference publishing and logs are wired. PRODUCTS, raw archival, price history, AI scoring, image clustering, supplier matching, all 4 direct integrations, automated schedule and production concurrency/idempotency remain TODO. Native page records are not eligible for publishing until verified and analyzed. No live data or credentials committed. API currently returns sheet cell strings. Test fixtures never enter production.
