from .topk import TopKStrategy
from .budget_topk import BudgetTopKStrategy
from .mmr import MMRStrategy
from .importance import ImportanceStrategy
from .summary import SummaryStrategy

ALL_STRATEGIES = [
    TopKStrategy,
    BudgetTopKStrategy,
    MMRStrategy,
    ImportanceStrategy,
    SummaryStrategy,
]
