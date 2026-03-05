"""
Elliptic AML API Integration.

Handles authentication, wallet screening, response parsing,
and markdown generation for AI consumption.

Supports demo mode via ELLIPTIC_DEMO_MODE=true environment variable.
"""

import hashlib
import hmac
import base64
import json
import os
import time
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ── Demo Data ──────────────────────────────────────────────────
# When ELLIPTIC_DEMO_MODE=true, these responses are used instead
# of calling the real API. They go through the same parser and
# markdown generator as real responses.

DEMO_RESPONSES = [
    # HIGH RISK — Score 10.0 — CSAM + Sanctions (Bitcoin)
    {
        "id": "demo-0001",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 4823000.00}, "outflow_value": {"usd": 4471000.00}}},
        "risk_score": 10.0,
        "risk_score_detail": {"source": 10.0, "destination": 4.2},
        "cluster_entities": [
            {"name": "Welcome To Video", "category": "CSAM", "is_primary_entity": True, "is_vasp": False, "is_after_sanction_date": None}
        ],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-01",
                    "rule_name": "Severe Illicit",
                    "risk_score": 10.0,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "CSAM",
                            "contribution_percentage": 34.2,
                            "contribution_value": {"usd": 1649460.00},
                            "counterparty_percentage": 12.1,
                            "counterparty_value": {"usd": 583383.00},
                            "indirect_percentage": 22.1,
                            "indirect_value": {"usd": 1066077.00},
                            "contributions": [
                                {
                                    "entity": "Welcome To Video",
                                    "contribution_percentage": 34.2,
                                    "contribution_value": {"usd": 1649460.00},
                                    "counterparty_percentage": 12.1,
                                    "counterparty_value": {"usd": 583383.00},
                                    "indirect_percentage": 22.1,
                                    "indirect_value": {"usd": 1066077.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 1,
                                    "risk_triggers": {"name": "Welcome To Video", "category": "CSAM", "is_sanctioned": False, "country": ["KR"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": [
                {
                    "rule_id": "demo-rule-02",
                    "rule_name": "Sanctions",
                    "risk_score": 8.5,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Sanctions",
                            "contribution_percentage": 18.7,
                            "contribution_value": {"usd": 835777.00},
                            "counterparty_percentage": 18.7,
                            "counterparty_value": {"usd": 835777.00},
                            "indirect_percentage": 0.0,
                            "indirect_value": {"usd": 0.0},
                            "contributions": [
                                {
                                    "entity": "Garantex",
                                    "contribution_percentage": 18.7,
                                    "contribution_value": {"usd": 835777.00},
                                    "counterparty_percentage": 18.7,
                                    "counterparty_value": {"usd": 835777.00},
                                    "indirect_percentage": 0.0,
                                    "indirect_value": {"usd": 0.0},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 1,
                                    "risk_triggers": {"name": "Garantex", "category": "Sanctions", "is_sanctioned": True, "country": ["RU"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ]
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Welcome To Video", "category": "CSAM", "is_primary_entity": True, "is_vasp": False}],
                    "contribution_percentage": 34.2,
                    "contribution_value": {"usd": 1649460.00},
                    "counterparty_percentage": 12.1,
                    "counterparty_value": {"usd": 583383.00},
                    "indirect_percentage": 22.1,
                    "indirect_value": {"usd": 1066077.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                },
                {
                    "entities": [{"name": "Hydra Market", "category": "Dark Market", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 11.4,
                    "contribution_value": {"usd": 549822.00},
                    "counterparty_percentage": 0.0,
                    "counterparty_value": {"usd": 0.0},
                    "indirect_percentage": 11.4,
                    "indirect_value": {"usd": 549822.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 3
                }
            ],
            "destination": [
                {
                    "entities": [{"name": "Garantex", "category": "Sanctions", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 18.7,
                    "contribution_value": {"usd": 835777.00},
                    "counterparty_percentage": 18.7,
                    "counterparty_value": {"usd": 835777.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                },
                {
                    "entities": [{"name": "OKX", "category": "Exchange", "is_primary_entity": False, "is_vasp": True}],
                    "contribution_percentage": 42.3,
                    "contribution_value": {"usd": 1891233.00},
                    "counterparty_percentage": 42.3,
                    "counterparty_value": {"usd": 1891233.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ]
        },
        "detected_behaviors": [
            {"behavior_type": "Peeling Chain", "length": 12, "usd_value": 234000.00}
        ],
        "process_status": "complete",
        "error": None
    },
    # HIGH RISK — Score 10.0 — Dark Market + Mixer (Bitcoin)
    {
        "id": "demo-0002",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 12750000.00}, "outflow_value": {"usd": 12680000.00}}},
        "risk_score": 10.0,
        "risk_score_detail": {"source": 10.0, "destination": 6.8},
        "cluster_entities": [
            {"name": "Hydra Market", "category": "Dark Market", "is_primary_entity": True, "is_vasp": False, "is_after_sanction_date": True}
        ],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-03",
                    "rule_name": "Illicit",
                    "risk_score": 10.0,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Dark Market",
                            "contribution_percentage": 67.3,
                            "contribution_value": {"usd": 8578750.00},
                            "counterparty_percentage": 67.3,
                            "counterparty_value": {"usd": 8578750.00},
                            "indirect_percentage": 0.0,
                            "indirect_value": {"usd": 0.0},
                            "contributions": [
                                {
                                    "entity": "Hydra Market",
                                    "contribution_percentage": 67.3,
                                    "contribution_value": {"usd": 8578750.00},
                                    "counterparty_percentage": 67.3,
                                    "counterparty_value": {"usd": 8578750.00},
                                    "indirect_percentage": 0.0,
                                    "indirect_value": {"usd": 0.0},
                                    "is_screened_address": True,
                                    "min_number_of_hops": 0,
                                    "risk_triggers": {"name": "Hydra Market", "category": "Dark Market", "is_sanctioned": True, "country": ["RU"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": [
                {
                    "rule_id": "demo-rule-04",
                    "rule_name": "Obfuscation",
                    "risk_score": 7.2,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Mixer",
                            "contribution_percentage": 28.9,
                            "contribution_value": {"usd": 3664520.00},
                            "counterparty_percentage": 14.2,
                            "counterparty_value": {"usd": 1800560.00},
                            "indirect_percentage": 14.7,
                            "indirect_value": {"usd": 1863960.00},
                            "contributions": [
                                {
                                    "entity": "Tornado Cash",
                                    "contribution_percentage": 28.9,
                                    "contribution_value": {"usd": 3664520.00},
                                    "counterparty_percentage": 14.2,
                                    "counterparty_value": {"usd": 1800560.00},
                                    "indirect_percentage": 14.7,
                                    "indirect_value": {"usd": 1863960.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 2,
                                    "risk_triggers": {"name": "Tornado Cash", "category": "Mixer", "is_sanctioned": True, "country": []}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ]
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Hydra Market", "category": "Dark Market", "is_primary_entity": True, "is_vasp": False}],
                    "contribution_percentage": 67.3,
                    "contribution_value": {"usd": 8578750.00},
                    "counterparty_percentage": 67.3,
                    "counterparty_value": {"usd": 8578750.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": True,
                    "min_number_of_hops": 0
                }
            ],
            "destination": [
                {
                    "entities": [{"name": "Tornado Cash", "category": "Mixer", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 28.9,
                    "contribution_value": {"usd": 3664520.00},
                    "counterparty_percentage": 14.2,
                    "counterparty_value": {"usd": 1800560.00},
                    "indirect_percentage": 14.7,
                    "indirect_value": {"usd": 1863960.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 2
                },
                {
                    "entities": [{"name": "Binance", "category": "Exchange", "is_primary_entity": False, "is_vasp": True}],
                    "contribution_percentage": 31.2,
                    "contribution_value": {"usd": 3956160.00},
                    "counterparty_percentage": 31.2,
                    "counterparty_value": {"usd": 3956160.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ]
        },
        "detected_behaviors": [
            {"behavior_type": "Peeling Chain", "length": 23, "usd_value": 890000.00},
            {"behavior_type": "Rapid Movement", "length": 5, "usd_value": 1200000.00}
        ],
        "process_status": "complete",
        "error": None
    },
    # HIGH RISK — Score 9.4 — Ransomware (Ethereum)
    {
        "id": "demo-0003",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "0x8589427373D6D84E98730D7795D8f6f8731FDA16", "blockchain": "ethereum"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 2340000.00}, "outflow_value": {"usd": 2295000.00}}},
        "risk_score": 9.4,
        "risk_score_detail": {"source": 9.4, "destination": 2.1},
        "cluster_entities": [
            {"name": "Conti Ransomware", "category": "Ransomware", "is_primary_entity": True, "is_vasp": False, "is_after_sanction_date": None}
        ],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-05",
                    "rule_name": "Severe Illicit",
                    "risk_score": 9.4,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Ransomware",
                            "contribution_percentage": 41.8,
                            "contribution_value": {"usd": 978120.00},
                            "counterparty_percentage": 22.5,
                            "counterparty_value": {"usd": 526500.00},
                            "indirect_percentage": 19.3,
                            "indirect_value": {"usd": 451620.00},
                            "contributions": [
                                {
                                    "entity": "Conti Ransomware",
                                    "contribution_percentage": 41.8,
                                    "contribution_value": {"usd": 978120.00},
                                    "counterparty_percentage": 22.5,
                                    "counterparty_value": {"usd": 526500.00},
                                    "indirect_percentage": 19.3,
                                    "indirect_value": {"usd": 451620.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 2,
                                    "risk_triggers": {"name": "Conti Ransomware", "category": "Ransomware", "is_sanctioned": False, "country": ["RU"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": []
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Conti Ransomware", "category": "Ransomware", "is_primary_entity": True, "is_vasp": False}],
                    "contribution_percentage": 41.8,
                    "contribution_value": {"usd": 978120.00},
                    "counterparty_percentage": 22.5,
                    "counterparty_value": {"usd": 526500.00},
                    "indirect_percentage": 19.3,
                    "indirect_value": {"usd": 451620.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 2
                },
                {
                    "entities": [{"name": "Unknown Cluster", "category": "Unknown", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 58.2,
                    "contribution_value": {"usd": 1361880.00},
                    "counterparty_percentage": 58.2,
                    "counterparty_value": {"usd": 1361880.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ],
            "destination": [
                {
                    "entities": [{"name": "KuCoin", "category": "Exchange", "is_primary_entity": False, "is_vasp": True}],
                    "contribution_percentage": 89.3,
                    "contribution_value": {"usd": 2049435.00},
                    "counterparty_percentage": 89.3,
                    "counterparty_value": {"usd": 2049435.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ]
        },
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # HIGH RISK — Score 6.0 — Gambling (Tron)
    {
        "id": "demo-0004",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "TN2YqTv4GVwyMFaqsvhEhC3SATt5rYWGjP", "blockchain": "tron"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 890000.00}, "outflow_value": {"usd": 845000.00}}},
        "risk_score": 6.0,
        "risk_score_detail": {"source": 6.0, "destination": 1.8},
        "cluster_entities": [],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-06",
                    "rule_name": "Gambling",
                    "risk_score": 6.0,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Gambling",
                            "contribution_percentage": 52.1,
                            "contribution_value": {"usd": 463690.00},
                            "counterparty_percentage": 38.4,
                            "counterparty_value": {"usd": 341760.00},
                            "indirect_percentage": 13.7,
                            "indirect_value": {"usd": 121930.00},
                            "contributions": [
                                {
                                    "entity": "Stake.com",
                                    "contribution_percentage": 31.2,
                                    "contribution_value": {"usd": 277680.00},
                                    "counterparty_percentage": 31.2,
                                    "counterparty_value": {"usd": 277680.00},
                                    "indirect_percentage": 0.0,
                                    "indirect_value": {"usd": 0.0},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 1,
                                    "risk_triggers": {"name": "Stake.com", "category": "Gambling", "is_sanctioned": False, "country": ["CW"]}
                                },
                                {
                                    "entity": "BC.Game",
                                    "contribution_percentage": 20.9,
                                    "contribution_value": {"usd": 186010.00},
                                    "counterparty_percentage": 7.2,
                                    "counterparty_value": {"usd": 64080.00},
                                    "indirect_percentage": 13.7,
                                    "indirect_value": {"usd": 121930.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 2,
                                    "risk_triggers": {"name": "BC.Game", "category": "Gambling", "is_sanctioned": False, "country": ["CW"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": []
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Stake.com", "category": "Gambling", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 31.2,
                    "contribution_value": {"usd": 277680.00},
                    "counterparty_percentage": 31.2,
                    "counterparty_value": {"usd": 277680.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                },
                {
                    "entities": [{"name": "BC.Game", "category": "Gambling", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 20.9,
                    "contribution_value": {"usd": 186010.00},
                    "counterparty_percentage": 7.2,
                    "counterparty_value": {"usd": 64080.00},
                    "indirect_percentage": 13.7,
                    "indirect_value": {"usd": 121930.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 2
                }
            ],
            "destination": [
                {
                    "entities": [{"name": "Bybit", "category": "Exchange", "is_primary_entity": False, "is_vasp": True}],
                    "contribution_percentage": 73.4,
                    "contribution_value": {"usd": 620230.00},
                    "counterparty_percentage": 73.4,
                    "counterparty_value": {"usd": 620230.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ]
        },
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # MEDIUM RISK — Score 4.2 — Gambling indirect (Bitcoin)
    {
        "id": "demo-0005",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 320000.00}, "outflow_value": {"usd": 318000.00}}},
        "risk_score": 4.2,
        "risk_score_detail": {"source": 4.2, "destination": 0.5},
        "cluster_entities": [
            {"name": "Unknown Wallet", "category": "Unknown", "is_primary_entity": True, "is_vasp": False, "is_after_sanction_date": None}
        ],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-07",
                    "rule_name": "Gambling",
                    "risk_score": 4.2,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Gambling",
                            "contribution_percentage": 8.3,
                            "contribution_value": {"usd": 26560.00},
                            "counterparty_percentage": 0.0,
                            "counterparty_value": {"usd": 0.0},
                            "indirect_percentage": 8.3,
                            "indirect_value": {"usd": 26560.00},
                            "contributions": [
                                {
                                    "entity": "Stake.com",
                                    "contribution_percentage": 8.3,
                                    "contribution_value": {"usd": 26560.00},
                                    "counterparty_percentage": 0.0,
                                    "counterparty_value": {"usd": 0.0},
                                    "indirect_percentage": 8.3,
                                    "indirect_value": {"usd": 26560.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 4,
                                    "risk_triggers": {"name": "Stake.com", "category": "Gambling", "is_sanctioned": False, "country": ["CW"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": []
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Stake.com", "category": "Gambling", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 8.3,
                    "contribution_value": {"usd": 26560.00},
                    "counterparty_percentage": 0.0,
                    "counterparty_value": {"usd": 0.0},
                    "indirect_percentage": 8.3,
                    "indirect_value": {"usd": 26560.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 4
                }
            ],
            "destination": []
        },
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # MEDIUM RISK — Score 3.8 — P2P / High Risk Exchange (Ethereum)
    {
        "id": "demo-0006",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "0x742d35Cc6634C0532925a3b844Bc9e7595f3aE12", "blockchain": "ethereum"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 1450000.00}, "outflow_value": {"usd": 1430000.00}}},
        "risk_score": 3.8,
        "risk_score_detail": {"source": 2.1, "destination": 3.8},
        "cluster_entities": [],
        "evaluation_detail": {
            "source": [],
            "destination": [
                {
                    "rule_id": "demo-rule-08",
                    "rule_name": "High Risk Exchange",
                    "risk_score": 3.8,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "High Risk Exchange",
                            "contribution_percentage": 15.2,
                            "contribution_value": {"usd": 217360.00},
                            "counterparty_percentage": 15.2,
                            "counterparty_value": {"usd": 217360.00},
                            "indirect_percentage": 0.0,
                            "indirect_value": {"usd": 0.0},
                            "contributions": [
                                {
                                    "entity": "Yobit",
                                    "contribution_percentage": 15.2,
                                    "contribution_value": {"usd": 217360.00},
                                    "counterparty_percentage": 15.2,
                                    "counterparty_value": {"usd": 217360.00},
                                    "indirect_percentage": 0.0,
                                    "indirect_value": {"usd": 0.0},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 1,
                                    "risk_triggers": {"name": "Yobit", "category": "High Risk Exchange", "is_sanctioned": False, "country": ["RU"]}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ]
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Binance", "category": "Exchange", "is_primary_entity": False, "is_vasp": True}],
                    "contribution_percentage": 91.2,
                    "contribution_value": {"usd": 1322400.00},
                    "counterparty_percentage": 91.2,
                    "counterparty_value": {"usd": 1322400.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ],
            "destination": [
                {
                    "entities": [{"name": "Yobit", "category": "High Risk Exchange", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 15.2,
                    "contribution_value": {"usd": 217360.00},
                    "counterparty_percentage": 15.2,
                    "counterparty_value": {"usd": 217360.00},
                    "indirect_percentage": 0.0,
                    "indirect_value": {"usd": 0.0},
                    "is_screened_address": False,
                    "min_number_of_hops": 1
                }
            ]
        },
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # MEDIUM RISK — Score 2.5 — Minor mixer indirect (Bitcoin)
    {
        "id": "demo-0007",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 78000.00}, "outflow_value": {"usd": 77500.00}}},
        "risk_score": 2.5,
        "risk_score_detail": {"source": 2.5, "destination": 0.0},
        "cluster_entities": [],
        "evaluation_detail": {
            "source": [
                {
                    "rule_id": "demo-rule-09",
                    "rule_name": "Obfuscation",
                    "risk_score": 2.5,
                    "rule_type": "exposure",
                    "matched_elements": [
                        {
                            "category": "Mixer",
                            "contribution_percentage": 3.1,
                            "contribution_value": {"usd": 2418.00},
                            "counterparty_percentage": 0.0,
                            "counterparty_value": {"usd": 0.0},
                            "indirect_percentage": 3.1,
                            "indirect_value": {"usd": 2418.00},
                            "contributions": [
                                {
                                    "entity": "Wasabi Wallet",
                                    "contribution_percentage": 3.1,
                                    "contribution_value": {"usd": 2418.00},
                                    "counterparty_percentage": 0.0,
                                    "counterparty_value": {"usd": 0.0},
                                    "indirect_percentage": 3.1,
                                    "indirect_value": {"usd": 2418.00},
                                    "is_screened_address": False,
                                    "min_number_of_hops": 5,
                                    "risk_triggers": {"name": "Wasabi Wallet", "category": "Mixer", "is_sanctioned": False, "country": []}
                                }
                            ]
                        }
                    ],
                    "matched_behaviors": []
                }
            ],
            "destination": []
        },
        "contributions": {
            "source": [
                {
                    "entities": [{"name": "Wasabi Wallet", "category": "Mixer", "is_primary_entity": False, "is_vasp": False}],
                    "contribution_percentage": 3.1,
                    "contribution_value": {"usd": 2418.00},
                    "counterparty_percentage": 0.0,
                    "counterparty_value": {"usd": 0.0},
                    "indirect_percentage": 3.1,
                    "indirect_value": {"usd": 2418.00},
                    "is_screened_address": False,
                    "min_number_of_hops": 5
                }
            ],
            "destination": []
        },
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.8 (Tron)
    {
        "id": "demo-0008",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "TVjsyZ7fYF3qLF6BQgPmTEZy1xrNNyVAAA", "blockchain": "tron"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 45000.00}, "outflow_value": {"usd": 44800.00}}},
        "risk_score": 0.8,
        "risk_score_detail": {"source": 0.8, "destination": 0.0},
        "cluster_entities": [],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.0 (Ethereum)
    {
        "id": "demo-0009",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "blockchain": "ethereum"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 892000000.00}, "outflow_value": {"usd": 891000000.00}}},
        "risk_score": 0.0,
        "risk_score_detail": {"source": 0.0, "destination": 0.0},
        "cluster_entities": [
            {"name": "Tether Treasury", "category": "Token Issuer", "is_primary_entity": True, "is_vasp": True, "is_after_sanction_date": None}
        ],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — null score (Bitcoin)
    {
        "id": "demo-0010",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 1200.00}, "outflow_value": {"usd": 1150.00}}},
        "risk_score": None,
        "risk_score_detail": {"source": None, "destination": None},
        "cluster_entities": [],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.3 (Tron)
    {
        "id": "demo-0011",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "TKMuG6K7Q8xdFru2WoYGKDJpBJmVFJ4wqq", "blockchain": "tron"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 23400.00}, "outflow_value": {"usd": 23100.00}}},
        "risk_score": 0.3,
        "risk_score_detail": {"source": 0.3, "destination": 0.0},
        "cluster_entities": [],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.0 (Ethereum)
    {
        "id": "demo-0012",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "0x28C6c06298d514Db089934071355E5743bf21d60", "blockchain": "ethereum"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 45200000.00}, "outflow_value": {"usd": 44800000.00}}},
        "risk_score": 0.0,
        "risk_score_detail": {"source": 0.0, "destination": 0.0},
        "cluster_entities": [
            {"name": "Binance", "category": "Exchange", "is_primary_entity": True, "is_vasp": True, "is_after_sanction_date": None}
        ],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.1 (Bitcoin)
    {
        "id": "demo-0013",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5", "blockchain": "bitcoin"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 5600.00}, "outflow_value": {"usd": 5400.00}}},
        "risk_score": 0.1,
        "risk_score_detail": {"source": 0.1, "destination": 0.0},
        "cluster_entities": [],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
    # LOW RISK — Score 0.0 (Tron)
    {
        "id": "demo-0014",
        "type": "wallet_exposure",
        "subject": {"asset": "holistic", "type": "address", "hash": "TAzsQ9Gx8eqFNFSKbeXrbi45CuVPHzA8wr", "blockchain": "tron"},
        "customer": {"id": "demo-cust-001", "reference": "DEMO_UID"},
        "blockchain_info": {"cluster": {"inflow_value": {"usd": 156000.00}, "outflow_value": {"usd": 155200.00}}},
        "risk_score": 0.0,
        "risk_score_detail": {"source": 0.0, "destination": 0.0},
        "cluster_entities": [],
        "evaluation_detail": {"source": [], "destination": []},
        "contributions": {"source": [], "destination": []},
        "detected_behaviors": [],
        "process_status": "complete",
        "error": None
    },
]


# ── Response Parser ────────────────────────────────────────────

def _classify_risk(score):
    """Classify risk score into HIGH/MEDIUM/LOW/NO DATA."""
    if score is None:
        return 'NO DATA'
    if score > 5.0:
        return 'HIGH'
    if score >= 2.0:
        return 'MEDIUM'
    return 'LOW'


def _fmt_usd(value):
    """Format USD value with commas and 2 decimal places."""
    if value is None:
        return '$0.00'
    if value >= 1_000_000:
        return '${:,.0f}'.format(value)
    return '${:,.2f}'.format(value)


def _extract_primary_entity(cluster_entities):
    """Find the primary entity from cluster_entities array."""
    if not cluster_entities:
        return None
    for e in cluster_entities:
        if e.get('is_primary_entity'):
            return {
                'name': e.get('name') or 'Unknown',
                'category': e.get('category') or 'Unknown',
                'is_vasp': e.get('is_vasp'),
            }
    # No primary flagged — use first
    e = cluster_entities[0]
    return {
        'name': e.get('name') or 'Unknown',
        'category': e.get('category') or 'Unknown',
        'is_vasp': e.get('is_vasp'),
    }


def _extract_typologies(evaluation_detail):
    """Extract typologies from evaluation_detail."""
    typologies = []
    if not evaluation_detail:
        return typologies
    for direction in ['source', 'destination']:
        rules = evaluation_detail.get(direction) or []
        for rule in rules:
            entities = []
            for me in (rule.get('matched_elements') or []):
                for contrib in (me.get('contributions') or []):
                    triggers = contrib.get('risk_triggers') or {}
                    entities.append({
                        'name': contrib.get('entity', 'Unknown'),
                        'hops': contrib.get('min_number_of_hops'),
                        'usd': (contrib.get('contribution_value') or {}).get('usd', 0),
                        'direct_usd': (contrib.get('counterparty_value') or {}).get('usd', 0),
                        'indirect_usd': (contrib.get('indirect_value') or {}).get('usd', 0),
                        'is_sanctioned': triggers.get('is_sanctioned', False),
                        'country': triggers.get('country', []),
                    })
            categories = []
            for me in (rule.get('matched_elements') or []):
                cat = me.get('category')
                if cat and cat not in categories:
                    categories.append(cat)
            typologies.append({
                'rule_name': rule.get('rule_name', 'Unknown'),
                'risk_score': rule.get('risk_score', 0),
                'direction': direction,
                'categories': categories,
                'entities': entities,
            })
    return typologies


def _extract_exposures(contributions):
    """Extract exposures from contributions object."""
    result = {'source': [], 'destination': []}
    if not contributions:
        return result
    for direction in ['source', 'destination']:
        items = contributions.get(direction) or []
        for item in items:
            entity_list = item.get('entities') or []
            entity_name = entity_list[0].get('name', 'Unknown') if entity_list else 'Unknown'
            entity_category = entity_list[0].get('category', 'Unknown') if entity_list else 'Unknown'
            result[direction].append({
                'entity': entity_name,
                'category': entity_category,
                'total_usd': (item.get('contribution_value') or {}).get('usd', 0),
                'direct_usd': (item.get('counterparty_value') or {}).get('usd', 0),
                'indirect_usd': (item.get('indirect_value') or {}).get('usd', 0),
                'hops': item.get('min_number_of_hops'),
                'is_screened_address': item.get('is_screened_address', False),
            })
    return result


def parse_response(raw, address_override=None):
    """
    Parse an Elliptic API response into standardised format.

    Args:
        raw: Dict from Elliptic API (or demo data).
        address_override: Override address (used in demo mode
                          when mapping demo responses to real addresses).

    Returns:
        Standardised result dict.
    """
    # Handle error state
    if raw.get('process_status') == 'error':
        return {
            'address': address_override or raw.get('subject', {}).get('hash', 'Unknown'),
            'chain': raw.get('subject', {}).get('blockchain', 'unknown'),
            'risk_score': None,
            'risk_score_source': None,
            'risk_score_destination': None,
            'risk_level': 'ERROR',
            'primary_entity': None,
            'typologies': [],
            'exposures': {'source': [], 'destination': []},
            'behaviors': [],
            'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
            'error': (raw.get('error') or {}).get('message', 'Unknown error'),
        }

    subject = raw.get('subject') or {}
    risk_score = raw.get('risk_score')
    risk_detail = raw.get('risk_score_detail') or {}
    blockchain_info = raw.get('blockchain_info') or {}
    cluster = blockchain_info.get('cluster') or {}

    behaviors = []
    for b in (raw.get('detected_behaviors') or []):
        behaviors.append({
            'type': b.get('behavior_type', 'Unknown'),
            'length': b.get('length', 0),
            'usd': b.get('usd_value', 0),
        })

    return {
        'address': address_override or subject.get('hash', 'Unknown'),
        'chain': subject.get('blockchain', 'unknown'),
        'risk_score': risk_score,
        'risk_score_source': risk_detail.get('source'),
        'risk_score_destination': risk_detail.get('destination'),
        'risk_level': _classify_risk(risk_score),
        'primary_entity': _extract_primary_entity(raw.get('cluster_entities')),
        'typologies': _extract_typologies(raw.get('evaluation_detail')),
        'exposures': _extract_exposures(raw.get('contributions')),
        'behaviors': behaviors,
        'cluster_flows': {
            'inflow_usd': (cluster.get('inflow_value') or {}).get('usd'),
            'outflow_usd': (cluster.get('outflow_value') or {}).get('usd'),
        },
        'error': None,
    }


# ── Markdown Generator ─────────────────────────────────────────

def generate_markdown(results, customer_id):
    """
    Generate structured markdown for AI consumption.

    Args:
        results: List of standardised result dicts from parse_response.
        customer_id: Binance UID.

    Returns:
        Markdown string.
    """
    from datetime import datetime

    high = [r for r in results if r['risk_level'] == 'HIGH']
    medium = [r for r in results if r['risk_level'] == 'MEDIUM']
    low = [r for r in results if r['risk_level'] in ('LOW', 'NO DATA')]
    errors = [r for r in results if r['risk_level'] == 'ERROR']

    lines = []
    lines.append('# Elliptic Wallet Screening Results')
    lines.append('')
    lines.append('**Customer ID:** {}'.format(customer_id))
    lines.append('**Date:** {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M UTC')))
    lines.append('**Addresses Screened:** {}'.format(len(results)))
    lines.append('')

    # Summary
    lines.append('## Summary')
    lines.append('')
    lines.append('- **HIGH RISK (>5.0):** {}'.format(len(high)))
    lines.append('- **MEDIUM RISK (2.0–5.0):** {}'.format(len(medium)))
    lines.append('- **LOW RISK (<2.0):** {}'.format(len(low)))
    if errors:
        lines.append('- **ERRORS:** {}'.format(len(errors)))
    lines.append('')

    # High risk detail
    if high:
        lines.append('## High Risk Addresses')
        lines.append('')
        for r in sorted(high, key=lambda x: (x['risk_score'] or 0), reverse=True):
            lines.append('### {}'.format(r['address']))
            lines.append('')

            # Score line
            score_parts = ['**Risk Score:** {}'.format(r['risk_score'])]
            if r['risk_score_source'] is not None or r['risk_score_destination'] is not None:
                score_parts.append('(source: {} / destination: {})'.format(
                    r['risk_score_source'] if r['risk_score_source'] is not None else 'N/A',
                    r['risk_score_destination'] if r['risk_score_destination'] is not None else 'N/A',
                ))
            lines.append('- ' + ' '.join(score_parts))

            # Chain
            lines.append('- **Chain:** {}'.format(r['chain']))

            # Entity
            if r['primary_entity']:
                pe = r['primary_entity']
                entity_str = '{} ({})'.format(pe['name'], pe['category'])
                if pe.get('is_vasp'):
                    entity_str += ' — VASP'
                lines.append('- **Primary Entity:** {}'.format(entity_str))

            # Typologies
            if r['typologies']:
                lines.append('- **Risk Triggers:**')
                for t in r['typologies']:
                    cat_str = ', '.join(t['categories']) if t['categories'] else 'N/A'
                    lines.append('  - {} (score: {}, direction: {}, categories: {})'.format(
                        t['rule_name'], t['risk_score'], t['direction'], cat_str))
                    for e in t['entities']:
                        sanctions_flag = ' **⚠ SANCTIONED**' if e.get('is_sanctioned') else ''
                        country_str = ''
                        if e.get('country'):
                            country_str = ' [{}]'.format(', '.join(e['country']))
                        lines.append('    - {} — {} hops — {} (direct: {} / indirect: {}){}{}'.format(
                            e['name'],
                            e['hops'] if e['hops'] is not None else '?',
                            _fmt_usd(e['usd']),
                            _fmt_usd(e['direct_usd']),
                            _fmt_usd(e['indirect_usd']),
                            country_str,
                            sanctions_flag,
                        ))

            # Exposures
            for direction in ['source', 'destination']:
                exps = r['exposures'].get(direction, [])
                dir_label = 'Source Exposures (funds FROM)' if direction == 'source' else 'Destination Exposures (funds TO)'
                if exps:
                    lines.append('- **{}:**'.format(dir_label))
                    for exp in exps:
                        screened_flag = ' [THIS WALLET]' if exp.get('is_screened_address') else ''
                        lines.append('  - {} ({}) — {} hops — {} (direct: {} / indirect: {}){}'.format(
                            exp['entity'],
                            exp['category'],
                            exp['hops'] if exp['hops'] is not None else '?',
                            _fmt_usd(exp['total_usd']),
                            _fmt_usd(exp['direct_usd']),
                            _fmt_usd(exp['indirect_usd']),
                            screened_flag,
                        ))
                else:
                    lines.append('- **{}:** None'.format(dir_label))

            # Behaviors
            if r['behaviors']:
                lines.append('- **Behavioral Patterns:**')
                for b in r['behaviors']:
                    lines.append('  - {} (length: {}, {})'.format(
                        b['type'], b['length'], _fmt_usd(b['usd'])))

            # Cluster flows
            if r['cluster_flows']['inflow_usd'] is not None:
                lines.append('- **Cluster Flows:** Inflow {} / Outflow {}'.format(
                    _fmt_usd(r['cluster_flows']['inflow_usd']),
                    _fmt_usd(r['cluster_flows']['outflow_usd']),
                ))

            lines.append('')

    # Medium risk table
    if medium:
        lines.append('## Medium Risk Addresses')
        lines.append('')
        lines.append('| Address | Chain | Score | Primary Entity | Top Typology |')
        lines.append('|---|---|---|---|---|')
        for r in sorted(medium, key=lambda x: (x['risk_score'] or 0), reverse=True):
            entity_str = r['primary_entity']['name'] if r['primary_entity'] else 'Unknown'
            top_typo = r['typologies'][0]['rule_name'] if r['typologies'] else 'N/A'
            addr_short = r['address'][:8] + '...' + r['address'][-6:]
            lines.append('| {} | {} | {} | {} | {} |'.format(
                addr_short, r['chain'], r['risk_score'], entity_str, top_typo))
        lines.append('')

        # Medium detail (condensed)
        lines.append('### Medium Risk Details')
        lines.append('')
        for r in sorted(medium, key=lambda x: (x['risk_score'] or 0), reverse=True):
            lines.append('**{}** (score: {}, chain: {})'.format(r['address'], r['risk_score'], r['chain']))
            for t in r['typologies']:
                for e in t['entities']:
                    sanctions_flag = ' SANCTIONED' if e.get('is_sanctioned') else ''
                    lines.append('- {} — {} ({}) — {} hops — {}{}'.format(
                        t['direction'].upper(), e['name'], ', '.join(t['categories']),
                        e['hops'] if e['hops'] is not None else '?',
                        _fmt_usd(e['usd']), sanctions_flag))
            lines.append('')

    # Low risk
    if low:
        lines.append('## Low Risk Addresses')
        lines.append('')
        lines.append('{} addresses with scores below 2.0 — no significant exposures detected.'.format(len(low)))
        lines.append('')
        for r in low:
            entity_str = ''
            if r['primary_entity']:
                entity_str = ' — {} ({})'.format(r['primary_entity']['name'], r['primary_entity']['category'])
            score_str = str(r['risk_score']) if r['risk_score'] is not None else 'null'
            lines.append('- `{}` ({}) score: {}{}'.format(
                r['address'], r['chain'], score_str, entity_str))
        lines.append('')

    # Errors
    if errors:
        lines.append('## Errors')
        lines.append('')
        for r in errors:
            lines.append('- `{}`: {}'.format(r['address'], r['error']))
        lines.append('')

    return '\n'.join(lines)


# ── Authentication ─────────────────────────────────────────────

def _sign_request(secret, timestamp, method, path, body_str):
    """
    Compute HMAC-SHA256 signature per Elliptic spec.

    Args:
        secret: Base64-encoded API secret.
        timestamp: Unix epoch milliseconds as string.
        method: HTTP method (uppercase).
        path: URL path (lowercase).
        body_str: JSON body as compact string.

    Returns:
        Base64-encoded signature string.
    """
    secret_bytes = base64.b64decode(secret)
    message = timestamp + method + path.lower() + body_str
    sig = hmac.new(secret_bytes, message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(sig.digest()).decode('utf-8')


# ── Screener Class ─────────────────────────────────────────────

class EllipticScreener:
    """
    Elliptic wallet screening client.

    Handles authentication, API calls, response parsing,
    and markdown generation. Supports demo mode.
    """

    def __init__(self):
        self.api_key = os.environ.get('ELLIPTIC_API_KEY', '')
        self.api_secret = os.environ.get('ELLIPTIC_API_SECRET', '')
        self.base_url = 'https://aml-api.elliptic.co'
        self.demo_mode = os.environ.get('ELLIPTIC_DEMO_MODE', '').lower() in ('true', '1', 'yes')

    def is_configured(self):
        """Check if API credentials are available or demo mode is on."""
        if self.demo_mode:
            return True
        return bool(self.api_key and self.api_secret)

    def _make_headers(self, method, path, body_str):
        """Build request headers with HMAC authentication."""
        timestamp = str(int(time.time() * 1000))
        signature = _sign_request(self.api_secret, timestamp, method, path, body_str)
        return {
            'Content-Type': 'application/json',
            'x-access-key': self.api_key,
            'x-access-sign': signature,
            'x-access-timestamp': timestamp,
        }

    def screen_address(self, address, customer_id):
        """
        Screen a single address via the Elliptic API.

        Returns standardised result dict.
        """
        if self.demo_mode:
            return self._demo_screen(address, customer_id)

        path = '/v2/wallet/synchronous'
        payload = {
            'subject': {
                'asset': 'holistic',
                'blockchain': 'holistic',
                'type': 'address',
                'hash': address,
            },
            'type': 'wallet_exposure',
            'customer_reference': customer_id,
        }
        body_str = json.dumps(payload, separators=(',', ':'))

        try:
            headers = self._make_headers('POST', path, body_str)
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url + path,
                    content=body_str,
                    headers=headers,
                )

            if response.status_code == 200:
                return parse_response(response.json())
            elif response.status_code == 404:
                return {
                    'address': address,
                    'chain': 'unknown',
                    'risk_score': None,
                    'risk_score_source': None,
                    'risk_score_destination': None,
                    'risk_level': 'NOT FOUND',
                    'primary_entity': None,
                    'typologies': [],
                    'exposures': {'source': [], 'destination': []},
                    'behaviors': [],
                    'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
                    'error': 'Address not found on blockchain',
                }
            elif response.status_code == 401:
                return {
                    'address': address,
                    'chain': 'unknown',
                    'risk_score': None,
                    'risk_score_source': None,
                    'risk_score_destination': None,
                    'risk_level': 'ERROR',
                    'primary_entity': None,
                    'typologies': [],
                    'exposures': {'source': [], 'destination': []},
                    'behaviors': [],
                    'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
                    'error': 'Authentication failed — check API key and secret',
                }
            else:
                error_body = response.text
                try:
                    error_json = response.json()
                    error_body = error_json.get('message', error_body)
                except Exception:
                    pass
                return {
                    'address': address,
                    'chain': 'unknown',
                    'risk_score': None,
                    'risk_score_source': None,
                    'risk_score_destination': None,
                    'risk_level': 'ERROR',
                    'primary_entity': None,
                    'typologies': [],
                    'exposures': {'source': [], 'destination': []},
                    'behaviors': [],
                    'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
                    'error': 'HTTP {} — {}'.format(response.status_code, error_body),
                }

        except httpx.TimeoutException:
            return {
                'address': address,
                'chain': 'unknown',
                'risk_score': None,
                'risk_score_source': None,
                'risk_score_destination': None,
                'risk_level': 'ERROR',
                'primary_entity': None,
                'typologies': [],
                'exposures': {'source': [], 'destination': []},
                'behaviors': [],
                'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
                'error': 'Request timed out',
            }
        except Exception as e:
            logger.exception('Elliptic API error for address %s', address)
            return {
                'address': address,
                'chain': 'unknown',
                'risk_score': None,
                'risk_score_source': None,
                'risk_score_destination': None,
                'risk_level': 'ERROR',
                'primary_entity': None,
                'typologies': [],
                'exposures': {'source': [], 'destination': []},
                'behaviors': [],
                'cluster_flows': {'inflow_usd': None, 'outflow_usd': None},
                'error': str(e),
            }

    def screen_batch(self, addresses, customer_id):
        """
        Screen multiple addresses. Does not stop on individual failures.

        Returns list of standardised result dicts.
        """
        results = []
        for address in addresses:
            result = self.screen_address(address, customer_id)
            results.append(result)
        return results

    def screen_and_report(self, addresses, customer_id):
        """
        Screen all addresses and generate complete report.

        Returns dict with summary, results, and markdown.
        """
        results = self.screen_batch(addresses, customer_id)

        high = sum(1 for r in results if r['risk_level'] == 'HIGH')
        medium = sum(1 for r in results if r['risk_level'] == 'MEDIUM')
        low = sum(1 for r in results if r['risk_level'] in ('LOW', 'NO DATA'))
        errors = sum(1 for r in results if r['risk_level'] in ('ERROR', 'NOT FOUND'))

        markdown = generate_markdown(results, customer_id)

        return {
            'status': 'complete',
            'demo_mode': self.demo_mode,
            'summary': {
                'total_screened': len(results),
                'high_risk': high,
                'medium_risk': medium,
                'low_risk': low,
                'errors': errors,
            },
            'results': results,
            'markdown': markdown,
        }

    def _demo_screen(self, address, customer_id):
        """
        Return demo data for an address.

        Maps real addresses to demo responses by index.
        Updates the customer_reference and address in the response.
        """
        # Pick a demo response based on address hash
        idx = hash(address) % len(DEMO_RESPONSES)
        raw = json.loads(json.dumps(DEMO_RESPONSES[idx]))  # deep copy

        # Override customer reference
        raw['customer']['reference'] = customer_id

        return parse_response(raw, address_override=address)