# Strategic Plan — Presentation Transcript (VN)

EAGLE EYE — STRATEGIC PLAN
TRANSCRIPT / KỊCH BẢN THUYẾT TRÌNH (Tiếng Việt)
Người nhận: Devon Rumpel — Sr. Director, Supply Chain Systems
Người trình: [Tên bạn] — Senior Product Owner, SC Analytics · GCC Vietnam

Ghi chú sử dụng: Mỗi mục dưới đây tương ứng một slide. Phần "NỘI DUNG SLIDE"
là những gì hiển thị trên màn hình; phần "LỜI DẪN" là gợi ý cách nói khi trình
bày. Bạn có thể đọc gần như nguyên văn hoặc diễn đạt lại theo phong cách của mình.

### Slide 1 — TRANG BÌA

**Nội Dung Slide:**
  Eagle Eye
  Từ 3.000 Dashboard đến Một Năng Lực Trí Tuệ Ra Quyết Định (Decision
  Intelligence Capability).
  Một chiến lược theo từng giai đoạn để xây dựng năng lực ra quyết định dựa
  trên AI, đáng tin cậy — chứng minh trước ở mảng forecast & inventory, và xây
  để mở rộng ra toàn chuỗi cung ứng Ashley.

**Lời Dẫn:**
  "Hôm nay tôi muốn trình bày với anh một kế hoạch chiến lược cho Eagle Eye.
  Đây không phải đề xuất làm thêm một công cụ báo cáo — mà là cách chúng ta
  thay đổi cách chuỗi cung ứng của Ashley ra quyết định. Tôi sẽ đi từ vấn đề,
  đến bản chất của Eagle Eye, lộ trình, và những gì tôi cần ở anh."

### Slide 2 — VẤN ĐỀ / VÌ SAO LÀ LÚC NÀY

**Nội Dung Slide:**
  "3.000 dashboard là vấn đề bề mặt. Adoption gần bằng 0 mới là nguyên nhân gốc rễ."
  - ~3.000 dashboard đang dùng — không bền vững để xây, sửa và đối soát.
  - ~0 mức độ sử dụng control tower hiện tại, dù nền dữ liệu mạnh.
  - 47% sai số dự báo (wMAPE) — quyết định dựa trên tín hiệu nhiễu.
  Con số này thực sự nói lên điều gì:
  - Một hố đen chi phí bảo trì: 3.000 view trên dữ liệu thiếu nhất quán = 3.000
    cuộc tranh cãi xem con số của ai mới đúng.
  - Dashboard như một cái nạng: mỗi câu hỏi mới lại đẻ ra một view, thay vì
    giải quyết quyết định.
  - Nhìn thấy được ≠ được sử dụng: ta không thiếu dữ liệu. Ta thiếu quyết định
    và niềm tin.
  - Bất khả thi khi mở rộng: mỗi SKU, kênh, khu vực mới không thể cứ tiếp tục
    sinh ra dashboard.

**Lời Dẫn:**
  "Điểm tôi muốn nhấn mạnh: con số 3.000 chỉ là vấn đề bề mặt. Vấn đề thật là dù
  nền dữ liệu của chúng ta mạnh, mức độ áp dụng control tower gần như bằng 0.
  Việc thêm dashboard đã được chứng minh là không cải thiện điều đó. Chúng ta
  không có vấn đề về dữ liệu — chúng ta có vấn đề về quyết định và niềm tin."

### Slide 3 — EAGLE EYE LÀ GÌ + ĐỊNH VỊ

**Nội Dung Slide:**
  "Không phải một công cụ — mà là một năng lực Trí tuệ Ra quyết định."
  Eagle Eye KHÔNG phải một dashboard, một report, một chatbot, một Copilot, một
  warehouse hay một UI. Đó là những thành phần có thể thay thế.

  Năng lực bền vững: khả năng biến một tình huống chuỗi cung ứng thành một quyết
  định được — ưu tiên, giải thích, tin cậy, hành động, và đo lường — hiện thực
  hóa qua các thành phần hôm nay, và có thể sống lâu hơn bất kỳ thành phần nào.

  Ranh giới scope — điều Eagle Eye KHÔNG làm: nó không sở hữu "transactional
  truth" — đó là việc của ERP và các hệ thống bản ghi. Eagle Eye là một hệ
  thống trí tuệ nằm bên trên, biến dữ liệu đáng tin thành quyết định.

  DNA của nó — năm động từ: Ưu tiên · Giải thích · Tin cậy · Hành động · Đo lường.

**Lời Dẫn:**
  "Đây là cách định vị quan trọng nhất. Eagle Eye là một NĂNG LỰC, không phải
  một công cụ. Copilot, Power BI, Fabric hay Databricks — tất cả đều có thể thay
  thế mà Eagle Eye vẫn còn nguyên. Điều này quan trọng vì nó quyết định cách ta
  đầu tư, đo lường và sở hữu nó — và nó bảo vệ chúng ta khỏi việc bị khóa vào
  một nhà cung cấp."

### Slide 4 — NĂNG LỰC ASHLEY ĐANG HƯỚNG TỚI

**Nội Dung Slide:**
  "Bộ năng lực — theo cách tôi hiểu, để anh hiệu chỉnh."
  (Đây là cách tôi hiểu định hướng cấp cao. Chỗ nào còn thiếu hoặc chưa đúng,
  góp ý của anh sẽ giúp làm sắc hơn.)
  - SEE (Nhìn): khả năng thấy real-time across demand, inventory, supply, orders
    & suppliers — một view đáng tin duy nhất.
  - SENSE (Cảm nhận): phát hiện sớm các ngoại lệ & bất thường, xếp hạng theo tác
    động kinh doanh, không theo số lượng cảnh báo.
  - EXPLAIN (Giải thích): truy nguyên nguyên nhân gốc — dịch chuyển demand, trễ
    supply, mất cân bằng — bằng ngôn ngữ dễ hiểu.
  - RECOMMEND (Đề xuất): đưa ra các hành động kế tiếp đã được xếp hạng và giải
    thích, kèm trade-off và độ tin cậy.
  - ACT (Hành động): đưa quyết định vào workflow — giao việc, phê duyệt, leo
    thang — và ghi lại.
  - LEARN (Học): theo dõi giá trị tạo ra, mức độ áp dụng và chất lượng quyết
    định; cải thiện theo thời gian.

**Lời Dẫn:**
  "Tôi cố tình trình bày slide này như một bản nháp để anh hiệu chỉnh. Đây là
  cách tôi hiểu các năng lực cấp cao mà chúng ta hướng tới. Nếu có chỗ nào tôi
  hiểu chưa đúng hoặc thiếu, đây là lúc lý tưởng để anh chỉnh hướng cho tôi."

### Slide 5 — LỘ TRÌNH: CÁC GIAI ĐOẠN & SẢN PHẨM BÀN GIAO

**Nội Dung Slide:**
  "Đánh giá trước khi xây, chứng minh trước khi mở rộng." (Trục: chiều sâu/thời
  gian)
  - Phase 1 — Discover & Assess: audit hiện trạng · lập bản đồ quyết định thật ·
    kiểm tra độ sẵn sàng dữ liệu.  Bàn giao: bản kiểm kê quyết định + danh sách
    rút gọn các domain beachhead.
  - Phase 2 — Foundation & Rationalize: KPI semantics · data gate · phân loại
    dashboard · quyết định nền tảng.  Bàn giao: phần "spine" dùng chung + kế
    hoạch phân loại.
  - Phase 3 — Beachhead MVP: một domain quyết định hẹp — chứng minh niềm tin &
    adoption.  Bàn giao: một decision service đã được tin cậy & sử dụng.
  - Phase 4 — Expand: áp dụng playbook đã được chứng minh sang các domain lân
    cận.  Bàn giao: phủ nhiều domain.
  - Phase 5 — Scale & Automate: quyết định xuyên domain + tự động hóa dần.  Bàn
    giao: năng lực cấp enterprise, sẵn sàng agentic.
  (Hai trục được tách bạch: slide này là chiều sâu — độ trưởng thành theo thời
  gian. Chiều rộng theo domain sẽ ở slide kế tiếp.)

**Lời Dẫn:**
  "Cách tiếp cận của tôi là có chủ đích: đánh giá trước khi xây, chứng minh
  trước khi mở rộng. Mỗi giai đoạn đều có sản phẩm bàn giao rõ ràng. Phần lớn
  giá trị và rủi ro được quyết định ở Phase 1 đến 3 — Phase 4 và 5 chỉ thành
  công nếu nền móng và niềm tin là thật."

### Slide 6 — CHÚNG TA ĐANG Ở ĐÂU

**Nội Dung Slide:**
  "Bạn đang ở đây — và điều gì mở khóa bước kế tiếp."
  Vạch tiến trình: [◆ CHÚNG TA Ở ĐÂY] Discover & Assess → Foundation &
  Rationalize → Beachhead MVP → Expand → Scale & Automate.

  Hôm nay: ngay đầu Phase 1. Requirements vẫn đang được thu thập. Chúng ta có
  nền chiến lược & dữ liệu mạnh, một PO đã được chỉ định (Lucas), và định hướng
  từ leadership — nhưng chưa có bản kiểm kê quyết định.

  Điều mở khóa bước kế tiếp: sự ủng hộ của anh với cách tiếp cận, một domain
  beachhead được chọn, và các quyết định về độ sẵn sàng dữ liệu + nền tảng — để
  việc khám phá Phase 1 có thể bắt đầu.

**Lời Dẫn:**
  "Trên tổng thể lộ trình, chúng ta đang ở vạch xuất phát của Phase 1. Chúng ta
  đã có nhiều thứ: chiến lược, dữ liệu, một PO, và định hướng. Cái còn thiếu —
  và là cái mở khóa bước tiếp theo — là quyết định của anh để chúng tôi chính
  thức bắt đầu khám phá."

### Slide 7 — DÀI HẠN: MỞ RỘNG ĐA DOMAIN + TÁC ĐỘNG KINH DOANH

**Nội Dung Slide:**
  "Một khuôn mẫu (pattern), áp dụng cho toàn chuỗi cung ứng." (Trục: chiều rộng)
  Eagle Eye mở rộng bằng cách đi theo dòng chảy quyết định của chính chuỗi cung
  ứng. Cùng một spine + playbook được tái sử dụng cho từng domain — domain thứ 2
  rẻ hơn domain thứ 1.

  Dòng chảy: Demand Planning → Inventory Management → Procurement → Manufacturing
  → Warehouse → Transportation → Customer Service.
  FINANCE — cắt ngang mọi domain (chi phí, biên lợi nhuận, vốn lưu động).
  (Beachhead = nơi dữ liệu sẵn sàng trước; Các domain sau = qua playbook lặp lại)

  Tác động kinh doanh:
  - wMAPE 47% → 30–38%
  - In-stock → 95% · excess → 5–10%
  - Giảm chi phí xây/bảo trì báo cáo

  Biên giới giá trị cao nhất:
  - Các quyết định xuyên domain mà không một dashboard đơn lẻ nào phục vụ được
    hôm nay.
  - Ví dụ "expedite hay chờ" động chạm cùng lúc tới 4 domain.
  - Giá trị cộng dồn khi Eagle Eye trải rộng qua các domain.

**Lời Dẫn:**
  "Đây là tham vọng dài hạn. Eagle Eye không chỉ giải bài toán forecast/inventory
  — nó mở rộng theo dòng chảy quyết định của doanh nghiệp, sang transportation,
  manufacturing, procurement, finance... Và điểm mấu chốt: giá trị cao nhất nằm
  ở các quyết định xuyên domain — những thứ mà hôm nay không một dashboard nào
  phục vụ nổi, planner phải mở năm cái view rồi ghép bằng tay."

### Slide 8 — ĐO LƯỜNG THÀNH CÔNG

**Nội Dung Slide:**
  "Adoption trước — rồi các kết quả kinh doanh sẽ theo sau."
  Leading — họ có đang dùng & tin nó không?
  - Mức sử dụng hằng tuần của planner so với công cụ cũ
  - Tỷ lệ câu trả lời từ Copilot được chấp nhận mà không cần kiểm tra lại thủ công
  - Số ngoại lệ được xử lý trong nền tảng (không qua email/Excel)
  - Số dashboard được khai tử so với baseline
  Lagging — quyết định có tốt hơn không?
  - Độ chính xác dự báo ↑ (wMAPE 47% → 30–38%), bias ↓
  - In-stock ↑ (→95%), excess stock ↓ (→5–10%)
  - Thời gian xử lý & tỷ lệ đóng ngoại lệ
  - Chi phí xây/bảo trì báo cáo ↓
  (Lỗi gốc trong quá khứ là xây những thứ không ai dùng. Nếu adoption không nhúc
  nhích, mọi thứ khác đều vô nghĩa.)

**Lời Dẫn:**
  "Tôi đặt adoption là thước đo hạng nhất, đặt TRƯỚC các metric kinh doanh. Lý
  do: lỗi gốc trong quá khứ của chúng ta là xây ra những thứ kỹ thuật tốt mà
  không ai dùng. Nên nếu mức độ sử dụng không tăng, thì dù forecast có chính xác
  đến đâu cũng không tạo ra giá trị."

### Slide 9 — YẾU TỐ KHÁC BIỆT: NIỀM TIN

**Nội Dung Slide:**
  "Niềm tin chính là sản phẩm — làm cho việc kiểm chứng gần như miễn phí."
  Planner là những người hoài nghi chuyên nghiệp — theo đúng bản chất nghề. Ta
  không chống lại điều đó — ta làm cho mỗi lần kiểm chứng rẻ tới mức chỉ còn là
  một cái liếc mắt. Vài trăm lần liếc-mà-thấy-đúng sẽ tạo ra niềm tin mà không
  một màn demo nào làm được.
  - Minh bạch (Transparency): cho thấy đường đi — mỗi con số lộ ra logic và
    nguồn, có thể truy xuống tận bản ghi.
  - Hiệu chỉnh (Calibration): gắn nhãn độ tin cậy. Một AI biết nói "chỗ này tôi
    không chắc" sẽ tạo niềm tin cho những câu nó chắc.
  - Nhất quán (Consistency): một câu hỏi, một con số — mọi lúc. KPI được quản trị
    tạo ra khả năng dự đoán.
  - Khả năng sửa (Correctability): cho người dùng báo lỗi và thấy nó được sửa —
    biến người hoài nghi thành người đồng xây.
  (Thứ tự quan trọng: assisted → recommended → touchless. Không bao giờ tự động
  hóa một quyết định giá trị cao trước khi niềm tin được tạo dựng.)

**Lời Dẫn:**
  "Đây là yếu tố tạo nên khác biệt, và cũng là điều dễ bị bỏ qua nhất. Năng lực
  này sẽ chết nếu planner không tin và không dùng. Nên niềm tin không phải tính
  năng phụ — nó CHÍNH LÀ sản phẩm. Mục tiêu không phải bắt họ ngừng kiểm tra, mà
  làm cho việc kiểm tra rẻ tới mức trở thành một cái liếc mắt tự nhiên."

### Slide 10 — THỰC THI: WORKSTREAMS, DECISION REGISTRY & VÍ DỤ

**Nội Dung Slide:**
  Tám workstreams:
  1–3. Khám phá · Lập bản đồ quyết định · xây Decision Registry
  4. Nền dữ liệu & KPI (semantic layer + cổng kiểm tra độ sẵn sàng)
  5. Phân loại dashboard — giữ / gộp / chuyển đổi / khai tử
  6. Nền tảng & decision services (exception, recommend, workflow)
  7. Niềm tin & adoption
  8. Quản trị & operating model

  Decision Registry — tài sản bền vững: một "pool" tool-agnostic chứa các quyết
  định lặp lại của Ashley — chủ sở hữu, trigger, đầu vào, logic, giá trị, độ
  trưởng thành. Tổ chức công việc bây giờ; grounding cho AI sau này.

  Một quyết định, từ đầu đến cuối:
  - Vấn đề kinh doanh: SKU có rủi ro — expedite hay chờ?
  - Quyết định: được ghi vào registry kèm trigger & đầu vào.
  - User story + tiêu chí: "Là một planner, tôi thấy các lựa chọn expedite được
    xếp hạng kèm trade-off chi phí/dịch vụ."
  - Validate bởi: nó có giải quyết đúng nhu cầu vận hành không? Adoption + chất
    lượng quyết định.

**Lời Dẫn:**
  "Phần thực thi gồm tám workstream. Trung tâm là Decision Registry — đây chính
  là insight quan trọng nhất: thay vì hỏi 'anh cần dashboard gì', ta hỏi 'anh
  đang cố ra quyết định gì, và hôm nay anh ra quyết định đó thế nào'. Câu hỏi đầu
  đẻ ra 3.000 dashboard; câu hỏi thứ hai kết thúc chúng. Bên phải là một ví dụ
  cụ thể chảy từ vấn đề kinh doanh tới user story và cách validate."

### Slide 11 — KIẾN TRÚC & TÍNH LINH HOẠT

**Nội Dung Slide:**
  "Năng lực sống lâu hơn bất kỳ thành phần đơn lẻ nào."
  Vì Eagle Eye là một năng lực, các thành phần của nó có thể thay thế. Decision
  Registry, KPI semantics và decision services giữ nguyên trong khi giao diện và
  nền tảng có thể thay đổi.
  - Lớp giao diện (Interface): Copilot hôm nay — có thể thay bằng UI/assistant
    bất kỳ.  [CÓ THỂ THAY THẾ]
  - Decision services: exception · recommendation · workflow · traceability.
    [BỀN VỮNG]
  - Decision Registry + KPI semantics: pool tri thức & định nghĩa metric được
    quản trị.  [BỀN VỮNG — XƯƠNG SỐNG]
  - Nền tảng dữ liệu (Data platform): Fabric hoặc Databricks · nền Golden Tables.
    [CÓ THỂ THAY THẾ]
  (Điều này bảo vệ Ashley khỏi vendor lock-in: quyết định Fabric vs Databricks,
  hay một thay đổi giao diện trong tương lai, không đòi hỏi phải phê duyệt lại
  năng lực.)

**Lời Dẫn:**
  "Đây là hệ quả trực tiếp của việc Eagle Eye là một năng lực. Lớp giao diện và
  nền tảng dữ liệu có thể thay thế; phần xương sống — Decision Registry và KPI
  semantics — thì bền vững. Nghĩa là quyết định Fabric hay Databricks không khóa
  chúng ta lại, và việc đổi Copilot sang giao diện khác sau này cũng không bắt
  ta phê duyệt lại từ đầu."

### Slide 12 — RỦI RO & GUARDRAILS

**Nội Dung Slide:**
  "Chúng ta gọi tên các kịch bản thất bại — và thiết kế để chặn từng cái."
  RỦI RO / PHỤ THUỘC                          →  GUARDRAIL CHÚNG TA XÂY
  - Ta xây ra dashboard #3.001 — xuất sắc       Adoption là metric hạng nhất;
    nhưng không ai dùng.                         beachhead hẹp, chứng minh có
                                                  người dùng trước khi mở rộng.
  - Planner không tin câu trả lời của AI.        Minh bạch + hiệu chỉnh + quyền
                                                  override ngay từ đầu; kiểm
                                                  chứng rẻ.
  - Xây trên dữ liệu chưa sẵn sàng (Golden       Một cổng data-readiness cứng;
    Tables).                                      neo vào Golden Tables, giới hạn
                                                  việc dùng EDW tạm thời.
  - Quá tải thay đổi ở các team nghiệp vụ.       Pilot, chứng minh, bảo vệ các
                                                  SME chủ chốt như đối tác; khai
                                                  tử theo giai đoạn, không big-bang.
  - AI/optimization trở thành "sidecar".         Nó phải nằm trong workflow hằng
                                                  ngày — lớp exception, KPI &
                                                  hành động dùng chung.
  - Cái "tạm thời" trở thành vĩnh viễn.          Các mốc redesign hậu-MVP rõ
                                                  ràng; MVP ≠ trạng thái cuối cùng.

**Lời Dẫn:**
  "Tôi chủ động gọi tên các kịch bản thất bại, vì phần lớn các dự án Decision
  Intelligence ở quy mô lớn đều thất bại. Với mỗi rủi ro, tôi đã có một guardrail
  tương ứng trong thiết kế sản phẩm. Nỗi sợ lớn nhất — và là nỗi sợ gốc — là
  chúng ta lại xây ra một dashboard nữa mà không ai dùng."

### Slide 13 — CON NGƯỜI, HỢP TÁC & ĐỀ NGHỊ

**Nội Dung Slide:**
  "Những gì chúng tôi cần từ anh để bắt đầu."
  Operating model & hợp tác:
  - PO + team: Lucas (PO) với SC Analytics — hiện 5 engineer, 0 PM. PO sở hữu
    intake & backlog.
  - Hợp tác chặt: business stakeholders, IT delivery, data teams, QA — cùng định
    nghĩa "done".
  - Giải quyết ưu tiên: PO phân xử các yêu cầu cạnh tranh; leo thang trade-off
    lên PM/leadership.
  - Quản trị: hội đồng sở hữu KPI & dữ liệu; các cổng trưởng thành
    assisted→touchless.

  Các quyết định chúng tôi cần ở anh:
  1. Ủng hộ cách tiếp cận theo giai đoạn — đánh giá & chứng minh trước khi mở rộng.
  2. Chọn beachhead mà anh ủng hộ (forecast hay inventory).
  3. Bảo trợ mandate về KPI-semantics & sở hữu dữ liệu.
  4. Định hướng thời điểm cho quyết định Fabric vs. Databricks.
  5. Xác nhận "adoption success" cần trông như thế nào.
  6. Hỗ trợ nguồn lực: một PM/PO đồng hành cùng team của Lucas.

**Lời Dẫn:**
  "Đây là phần đề nghị cụ thể. Bên trái là cách chúng tôi sẽ vận hành và hợp tác.
  Bên phải là sáu quyết định mà chỉ anh mới có thể đưa ra để mở khóa Phase 1.
  Tôi muốn kết thúc bằng một lời đề nghị rõ ràng, chứ không phải chỉ là thông
  tin."

### Slide 14 — TÓM TẮT SÁNG KIẾN (THEO FORMAT ASHLEY)

**Nội Dung Slide:**
  "Eagle Eye theo format sáng kiến của Ashley."
  - Problem Statement: Adoption control tower gần bằng 0 dù nền dữ liệu mạnh;
    ~3.000 dashboard không bền vững và quyết định vẫn chậm, bị động, đối soát thủ
    công.
  - Strategic Objective: Một hệ thống ra quyết định AI-First cho chuỗi cung ứng —
    hỗ trợ AI-First Org, Network of the Future & Advanced Automation; chuyển từ
    báo cáo sang quyết định.
  - Initiative Description: Xây một năng lực Decision Intelligence (Copilot-first)
    trên nền dữ liệu + KPI được quản trị; chứng minh ở forecast/inventory, mở
    rộng ra các domain.
  - Key Metrics: Adoption (trước hết); wMAPE 47%→30–38%; in-stock→95%;
    excess→5–10%; thời gian xử lý ngoại lệ; số dashboard khai tử; chi phí báo
    cáo ↓.
  - Risks / Dependencies: Niềm tin vào AI; độ sẵn sàng Golden Tables; quá tải
    thay đổi; Fabric vs Databricks; tránh "sidecar analytics" & dashboard #3.001.
  - What We'll Need: Bảo trợ từ lãnh đạo; PO + PM & team SC Analytics; hợp tác
    business/IT/data/QA; quản trị dữ liệu & KPI; quyết định nền tảng.

**Lời Dẫn:**
  "Để khép lại, đây là toàn bộ Eagle Eye gói gọn trong đúng format sáng kiến mà
  Ashley vẫn dùng — Problem Statement, Strategic Objective, Initiative
  Description, Key Metrics, Risks/Dependencies, và What We'll Need. Tôi hy vọng
  nó giúp anh đặt Eagle Eye cạnh các sáng kiến khác và đánh giá một cách công
  bằng. Tôi rất mong nhận được phản hồi và định hướng từ anh."

HẾT TRANSCRIPT — 14 SLIDE
Ghi chú: Nhớ điền [Tên bạn] ở Slide 1 & 13, và rà lại tên/chức danh trước khi
trình bày.
