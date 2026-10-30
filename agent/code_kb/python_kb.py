"""Python snippets (each one runs as-is)."""

SNIPPETS = {
    "hello_world": r'''print("Hello, World!")''',
    "variables": r'''
name = "Sara"
age = 25
pi = 3.14
is_active = True
print(name, age, pi, is_active)''',
    "if_else": r'''
age = 20
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teen")
else:
    print("Child")''',
    "for_loop": r'''
for i in range(5):
    print(i)

for fruit in ["apple", "banana"]:
    print(fruit)''',
    "while_loop": r'''
count = 0
while count < 5:
    print(count)
    count += 1''',
    "function": r'''
def add(a, b):
    return a + b

print(add(2, 3))  # 5''',
    "list": r'''
nums = [3, 1, 2]
nums.append(4)
print(nums[0], len(nums))  # 3 4''',
    "dict": r'''
ages = {"Ali": 30, "Sara": 25}
ages["Omar"] = 22
for name, age in ages.items():
    print(name, age)''',
    "class": r'''
class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hi, I'm {self.name}"

print(Person("Ali").greet())''',
    "read_file": r'''
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
print(content)''',
    "write_file": r'''
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("Hello file\n")''',
    "reverse_string": r'''
text = "hello"
print(text[::-1])  # olleh''',
    "sort_list": r'''
nums = [5, 2, 9, 1]
print(sorted(nums))                # [1, 2, 5, 9]
print(sorted(nums, reverse=True))  # [9, 5, 2, 1]''',
    "try_catch": r'''
try:
    x = 10 / 0
except ZeroDivisionError as e:
    print("Error:", e)
finally:
    print("done")''',
    "http_request": r'''
import json
import urllib.request

with urllib.request.urlopen("https://api.github.com") as response:
    data = json.load(response)
print(response.status, list(data)[:3])''',
    "json_parse": r'''
import json

data = json.loads('{"name": "Ali", "age": 30}')
print(data["name"])               # Ali
print(json.dumps(data, indent=2))''',
    "random_number": r'''
import random

print(random.randint(1, 100))         # 1..100
print(random.choice(["a", "b", "c"]))''',
    "current_date": r'''
from datetime import datetime

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M"))''',
    "split_string": r'''
parts = "a,b,c".split(",")
print(parts)            # ['a', 'b', 'c']
print("-".join(parts))  # a-b-c''',
    "sum_max": r'''
nums = [4, 8, 15]
print(sum(nums), max(nums), min(nums))  # 27 15 4''',
}
