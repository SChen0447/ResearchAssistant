import random 
import uuid
from locust import HttpUser, between, task

QUESTIONS = [
    "什么是贝叶斯公式？",
    "请解释极大似然估计",
    "支持向量机的核心原理是什么？",
    "什么是过拟合与欠拟合？",
    "决策树如何计算信息增益？",
    "k近邻算法有什么优缺点？",
    "请介绍梯度下降法",
    "集成学习中Bagging和Boosting的区别",
    "主成分分析PCA的作用是什么？",
    "什么是交叉验证？",
]


class ResearchAssistantUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def ask(self):
        payload = {
            "user_id": "loadtest_user",
            "session_id": str(uuid.uuid4()),
            "question": random.choice(QUESTIONS),
        }
        with self.client.post(
            "/research_assistant/ask",
            json=payload,
            name="/research_assistant/ask",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")

    @task(1)
    def health(self):
        self.client.get("/research_assistant/health", name="/research_assistant/health")










