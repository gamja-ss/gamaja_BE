def calculate_user_tier(exp):
    TIERS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Master"]
    exp_per_tier = 50
    exp_per_level = 10

    if exp >= len(TIERS) * exp_per_tier:
        return "Master"

    tier_index = exp // exp_per_tier
    tier = TIERS[tier_index]

    if tier == "Master":
        return tier

    level = 5 - ((exp % exp_per_tier) // exp_per_level)
    return f"{tier}{level}"
