"""
冗余检测器 - 识别相似查询
"""

from typing import List
from difflib import SequenceMatcher


class RedundancyDetector:
    """
    检测查询冗余
    
    Agent 的查询有 80-90% 的冗余，我们可以识别并共享计算
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.threshold = similarity_threshold
        self.query_history = []
    
    def add_query(self, query: str):
        """添加查询到历史"""
        self.query_history.append(query)
    
    def find_similar(self, query: str) -> List[tuple]:
        """
        查找相似查询
        
        Returns:
            List[tuple]: [(相似查询, 相似度得分)]
        """
        similar = []
        
        for hist_query in self.query_history:
            similarity = self._calculate_similarity(query, hist_query)
            if similarity >= self.threshold:
                similar.append((hist_query, similarity))
        
        # 按相似度排序
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """计算两个查询的相似度"""
        return SequenceMatcher(None, query1.lower(), query2.lower()).ratio()
    
    def get_redundancy_rate(self) -> float:
        """计算冗余率"""
        if len(self.query_history) < 2:
            return 0.0
        
        redundant_count = 0
        for i, query in enumerate(self.query_history):
            for other_query in self.query_history[:i]:
                if self._calculate_similarity(query, other_query) >= self.threshold:
                    redundant_count += 1
                    break
        
        return redundant_count / len(self.query_history)

