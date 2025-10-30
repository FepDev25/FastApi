"""
- You have $50
- You buy an item that is $15
- With a tax of 3%
- print how much money you have left
"""

money = 50
item_price = 15
tax_rate = 0.03

money_left = money - (item_price + (item_price * tax_rate))
print(money_left)
