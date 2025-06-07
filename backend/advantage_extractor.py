from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

CANDIDATE_STRENGTHS = [
    "노력함", "포기하지 않음", "자신을 돌아봄", "실패를 받아들임", "긍정적인 태도",
    "새로운 것을 시도함", "감정을 솔직하게 표현함", "성장을 시도함"
]

STRENGTH_DESCRIPTIONS = {
    "노력함": "잘하고자 노력했고",
    "포기하지 않음": "쉽지 않아도 포기하지 않았으며",
    "자신을 돌아봄": "자신을 돌아보는 시간을 가졌고",
    "실패를 받아들임": "실패를 있는 그대로 받아들였으며",
    "긍정적인 태도": "긍정적인 태도를 유지했고",
    "새로운 것을 시도함": "새로운 것을 시도했으며",
    "감정을 솔직하게 표현함": "자신의 감정을 솔직히 표현했고",
    "성장을 시도함": "성장을 위한 노력을 했습니다"
}

NEGATIVE_EMOTIONS = ['짜증', '화남', '속상함', '우울함', '불쾌함', '피곤함']

def extract_advantages(text):
    """
    일기 내용에서 장점 후보군과 비교하여 상위 장점 추출.
    부정확한 추출(예: 포기하지 않음의 남용)을 줄이기 위해 보정 로직 포함.
    """
    result = classifier(text, CANDIDATE_STRENGTHS, multi_label=True)

    candidates = [
        (label, score) for label, score in zip(result["labels"], result["scores"])
        if score > 0.25
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)
    top = candidates[:5]

    adjusted = []
    for label, score in top:
        if label == "포기하지 않음" and score < 0.45:
            continue
        adjusted.append(label)

    return adjusted[:3] if adjusted else ["긍정적인 태도"]


def format_advantages_paragraph(strengths):
    phrases = [STRENGTH_DESCRIPTIONS.get(s, s) for s in strengths]
    if not phrases:
        return "장점이 분석되지 않았습니다."
    return "당신은 오늘 " + ", ".join(phrases[:-1]) + (" 그리고 " + phrases[-1] if len(phrases) > 1 else phrases[0]) + "."
