import sys
from pathlib import Path
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def extract_good_points(review):
    prompt = f"Trích xuất các điểm tốt của sản phẩm từ đánh giá sau: '{review}'. Trả về mỗi good point là một dòng."
    return llm(prompt, model="cheap", provider="openai")
def extract_bad_points(review):
    prompt = f"Trích xuất các điểm xấu của sản phẩm từ đánh giá sau: '{review}'. Trả về mỗi bad point là một dòng."
    return llm(prompt, model="cheap", provider="openai")
def contain_toxic_language(review):
    prompt = f"Kiểm tra xem đánh giá sau có chứa ngôn ngữ độc hại hay không: '{review}'. Chỉ trả về 'YES' hoặc 'NO'."
    return llm(prompt, model="cheap", provider="openai")


def aggregate_reviews(good_points, bad_points, toxic_language):
    # combine good and bad points into a json structure
    return {
        "tot": good_points,
        "xau": bad_points,
        "doc_hai": toxic_language
    }

def pipeline(review):
    #using concurrent.futures.ThreadPoolExecutor

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_good = executor.submit(extract_good_points, review)
        future_bad = executor.submit(extract_bad_points, review)
        future_toxic = executor.submit(contain_toxic_language, review)

        good_points = future_good.result().splitlines()
        bad_points = future_bad.result().splitlines()
        toxic_language = future_toxic.result()

    result = aggregate_reviews(good_points, bad_points, toxic_language)
    return result

if __name__ == "__main__":
    review = "Mình mới tậu cái tai nghe Bluetooth dòng X này tuần trước. Phải công nhận là chất âm khá ngon, bass đập cực kỳ lực nghe nhạc EDM rất sướng, pin lại trâu xài liên tục 3 ngày chưa thấy báo hết. Nhưng mà cái phần mềm điều khiển trên điện thoại thì thiết kế ngu học đéo chịu được. Đang nghe nhạc tự nhiên app bị đơ, kết nối Bluetooth thì chập chờn bực hết cả mình. Chưa kể thiết kế mút tai khá cứng, đeo tầm hơn một tiếng là đau ép hết cả vành tai. Bỏ ra hơn củ bạc mua về rước cục tức vào người, hãng làm ăn như hạch!"
    result = pipeline(review)
    print(result)

    
