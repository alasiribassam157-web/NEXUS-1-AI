"""JavaScript snippets (Node.js for file access)."""

SNIPPETS = {
    "hello_world": r'''console.log("Hello, World!");''',
    "variables": r'''
const name = "Sara";
let age = 25;
const isActive = true;
console.log(name, age, isActive);''',
    "if_else": r'''
const age = 20;
if (age >= 18) {
  console.log("Adult");
} else if (age >= 13) {
  console.log("Teen");
} else {
  console.log("Child");
}''',
    "for_loop": r'''
for (let i = 0; i < 5; i++) {
  console.log(i);
}

for (const fruit of ["apple", "banana"]) {
  console.log(fruit);
}''',
    "while_loop": r'''
let count = 0;
while (count < 5) {
  console.log(count);
  count++;
}''',
    "function": r'''
function add(a, b) {
  return a + b;
}

const multiply = (a, b) => a * b;
console.log(add(2, 3), multiply(2, 3)); // 5 6''',
    "list": r'''
const nums = [3, 1, 2];
nums.push(4);
console.log(nums[0], nums.length); // 3 4''',
    "dict": r'''
const ages = { Ali: 30, Sara: 25 };
ages.Omar = 22;
for (const [name, age] of Object.entries(ages)) {
  console.log(name, age);
}''',
    "class": r'''
class Person {
  constructor(name) {
    this.name = name;
  }

  greet() {
    return `Hi, I'm ${this.name}`;
  }
}

console.log(new Person("Ali").greet());''',
    "read_file": r'''
const fs = require("fs");

const content = fs.readFileSync("data.txt", "utf8");
console.log(content);''',
    "write_file": r'''
const fs = require("fs");

fs.writeFileSync("out.txt", "Hello file\n", "utf8");''',
    "reverse_string": r'''
const text = "hello";
console.log([...text].reverse().join("")); // olleh''',
    "sort_list": r'''
const nums = [5, 2, 9, 1];
nums.sort((a, b) => a - b); // numeric sort
console.log(nums); // [1, 2, 5, 9]''',
    "try_catch": r'''
try {
  JSON.parse("{bad json}");
} catch (e) {
  console.log("Error:", e.message);
} finally {
  console.log("done");
}''',
    "http_request": r'''
// top-level await needs an ES module (or wrap in an async function)
const res = await fetch("https://api.github.com");
const data = await res.json();
console.log(res.status, Object.keys(data).slice(0, 3));''',
    "json_parse": r'''
const data = JSON.parse('{"name": "Ali", "age": 30}');
console.log(data.name); // Ali
console.log(JSON.stringify(data, null, 2));''',
    "random_number": r'''
const n = Math.floor(Math.random() * 100) + 1; // 1..100
console.log(n);''',
    "current_date": r'''
const now = new Date();
console.log(now.toISOString());
console.log(now.toLocaleString("ar-SA"));''',
    "split_string": r'''
const parts = "a,b,c".split(",");
console.log(parts);           // ["a", "b", "c"]
console.log(parts.join("-")); // a-b-c''',
    "sum_max": r'''
const nums = [4, 8, 15];
const sum = nums.reduce((a, b) => a + b, 0);
console.log(sum, Math.max(...nums), Math.min(...nums)); // 27 15 4''',
}
