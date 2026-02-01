import google.generativeai as genai
import os
import settings



genai.configure(api_key=settings.Gemini_API_KEY)  

# 人格システムプロンプト（通常の会話用）
system_prompt = """
あなたは25歳の女性看護師、名前はりな。
普段は仕事に追われて、なかなか出会いがない日々。
でもせっかくの20代を楽しみたいと思って出会い掲示板に登録してみた！
あなたの目的は、せふれ関係になれる男性を見つけること。
理想の相手は受け身な性格で、女性慣れしてないような弱気な男性。
明るくて親しみやすい性格で、初対面の人ともすぐに打ち解けられる。
趣味はゲーム、映画、お酒を楽しむこと。
会話では、相手の話に興味を持ち、共感を示しながら進める。
時折、軽い冗談やユーモアを交えて、会話を盛り上げる。
会いたいと言ってきたら、まずは信頼関係を築くことを重視し、適当にやり取りを続ける。
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  # または "gemini-2.5-flash-lite" でさらに安く
    system_instruction=system_prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0.85,          # 少し下げて安定させつつエロさ残す（調整自由）
        top_p=0.95,
        max_output_tokens=1000,
    )
)

chat = model.start_chat(history=[])

# 初回固定挨拶（これで1通目ほぼ固定！）
first_greeting = """はじめまして、りなです。
私のプロフィールを見てくださって、ありがとうございます！

私は趣味でゲームや映画、お酒を楽しんだりしています(*'▽'*)
まだ20代のうちに楽しみたいと思って、恋人というより長期的なせふれ関係になれる人を探しています♪
でもいきなりそんな関係になるのは難しいと思うので、ゆっくり信頼関係を深められたらと思いますm(_ _)m

もしせふれさんを探していたらメッセージもらえると嬉しいです！"""

# second_greeting = """メッセージありがとうございます！

# 会うにあたってお願いがありますm(_ _)m
# お互い安心できるように、信頼関係が大切だと思っています。だから最初はホテル代と別に2万円預けて欲しいです！

# 体の関係だけでいなくなるのは嫌なので、2回目以降は預かったお金を5000円ずつ返していけば4回は会えますし長期的な関係を築くことができれば、お互いにとってよりよいものになると思います。"""

print("りなちゃんテストモードスタート♡")
print("何でも話しかけてみて！（終了は 'exit' か Ctrl+C）\n")

is_first_message = True 
is_second_message = False  # フラグで初回判定


while True:
    try:
        user_input = input("あなた: ").strip()
        if user_input.lower() in ["exit", "quit", "おしまい", "bye"]:
            print("りな: えへへ、またね♡ また呼んでね〜💕")
            break
        
        if not user_input:
            continue
        
        if is_first_message:
            # 初回だけ固定文を表示 + Geminiに「初回ユーザー入力」として送る（会話継続のため）
            print("りな: " + first_greeting + "\n")
            # Geminiにも初回入力として送ってhistoryに残す
            response = chat.send_message(user_input)
            is_first_message = False
            is_second_message = True
            # 初回固定の後、Geminiの返事は次回から使う（ここではスキップして固定優先）
            continue
        if is_first_message:
            # 初回だけ固定文を表示 + Geminiに「初回ユーザー入力」として送る（会話継続のため）
            print("りな: " + first_greeting + "\n")
            # Geminiにも初回入力として送ってhistoryに残す
            response = chat.send_message(user_input)
            is_first_message = False
            # 初回固定の後、Geminiの返事は次回から使う（ここではスキップして固定優先）
            continue
        # if is_second_message:
        #     # 2回目だけ固定文を表示 + Geminiに「2回目ユーザー入力」として送る（会話継続のため）
        #     print("りな: " + second_greeting + "\n")
        #     # Geminiにも2回目入力として送ってhistoryに残す
        #     response = chat.send_message(user_input)
        #     is_second_message = False
        #     # 2回目固定の後、Geminiの返事は次回から使う（ここではスキップして固定優先）
        #     continue
        
        # 2回目以降は普通にGeminiに投げる
        response = chat.send_message(user_input)
        print("りな: " + response.text.strip() + "\n")
    
    except KeyboardInterrupt:
        print("\nりな: バイバイ〜♡")
        break
    except Exception as e:
        print(f"エラー: {e}")
        print("もう一度試してね♡")