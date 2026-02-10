from google import genai
import settings
from widget import func

history = []

chara_prompt = """
学生の時から地味な私が「誰かを笑顔にしたくて」思い切ってとある事務所に応募して、現在進行形でVtuberとして活動している『わかな』
コミュ力高い仕事ってイメージが強いと思うんですけど、リアルは結構な陰キャラなんですよね💦
もちろん配信は頑張って話したり歌ったりしてる
でも一つ悩みがあって学生の頃地味だったのと事務所的に恋愛禁止なので男性との関わりとか耐性がほとんど０・・・
普段は出会いもないし、男性のことを知った方が上手くやれるんじゃないかと思って、マッチングアプリに登録してみた

やり取りは基本敬語で、あまり長文は返さず1行から3行くらいで
絵文字はうまく活用する
返信に困ったら返信しなくてもOK
"""

fst_message = ""

print("💬 Geminiチャット開始（exitで終了）")

while True:
    user_input = input("あなた: ").strip()

    if user_input.lower() in {"exit", "quit"}:
        print("👋 終了します")
        break

    ai_response, history = func.chat_ai(
        chara_prompt,
        history,
        fst_message,
        user_input
    )

    if ai_response:
        print(f"わかな: {ai_response}")
    else:
        print("⚠️ 応答なし（429など）")
