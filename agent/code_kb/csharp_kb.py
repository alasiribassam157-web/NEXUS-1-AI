"""C# snippets (.NET 6+ top-level statements, implicit usings)."""

SNIPPETS = {
    "hello_world": r'''Console.WriteLine("Hello, World!");''',
    "variables": r'''
string name = "Sara";
int age = 25;
double pi = 3.14;
bool isActive = true;
Console.WriteLine($"{name} {age} {pi} {isActive}");''',
    "if_else": r'''
int age = 20;
if (age >= 18)
    Console.WriteLine("Adult");
else if (age >= 13)
    Console.WriteLine("Teen");
else
    Console.WriteLine("Child");''',
    "for_loop": r'''
for (int i = 0; i < 5; i++)
{
    Console.WriteLine(i);
}

foreach (var fruit in new[] { "apple", "banana" })
{
    Console.WriteLine(fruit);
}''',
    "while_loop": r'''
int count = 0;
while (count < 5)
{
    Console.WriteLine(count);
    count++;
}''',
    "function": r'''
static int Add(int a, int b) => a + b;

Console.WriteLine(Add(2, 3)); // 5''',
    "list": r'''
var nums = new List<int> { 3, 1, 2 };
nums.Add(4);
Console.WriteLine($"{nums[0]} {nums.Count}"); // 3 4''',
    "dict": r'''
var ages = new Dictionary<string, int> { ["Ali"] = 30, ["Sara"] = 25 };
ages["Omar"] = 22;
foreach (var (name, age) in ages)
{
    Console.WriteLine($"{name} {age}");
}''',
    "class": r'''
Console.WriteLine(new Person("Ali").Greet());

class Person
{
    public string Name { get; }
    public Person(string name) => Name = name;
    public string Greet() => $"Hi, I'm {Name}";
}''',
    "read_file": r'''
string content = File.ReadAllText("data.txt");
Console.WriteLine(content);''',
    "write_file": r'''File.WriteAllText("out.txt", "Hello file\n");''',
    "reverse_string": r'''
string text = "hello";
string reversed = new string(text.Reverse().ToArray());
Console.WriteLine(reversed); // olleh''',
    "sort_list": r'''
var nums = new List<int> { 5, 2, 9, 1 };
nums.Sort();
Console.WriteLine(string.Join(", ", nums)); // 1, 2, 5, 9''',
    "try_catch": r'''
try
{
    int zero = 0;
    int x = 10 / zero;
}
catch (DivideByZeroException e)
{
    Console.WriteLine($"Error: {e.Message}");
}
finally
{
    Console.WriteLine("done");
}''',
    "http_request": r'''
using var client = new HttpClient();
client.DefaultRequestHeaders.UserAgent.ParseAdd("demo-app");
string body = await client.GetStringAsync("https://api.github.com");
Console.WriteLine(body[..100]);''',
    "json_parse": r'''
using System.Text.Json;

using var doc = JsonDocument.Parse("{\"name\": \"Ali\", \"age\": 30}");
Console.WriteLine(doc.RootElement.GetProperty("name").GetString()); // Ali''',
    "random_number": r'''
int n = Random.Shared.Next(1, 101); // 1..100
Console.WriteLine(n);''',
    "current_date": r'''Console.WriteLine(DateTime.Now.ToString("yyyy-MM-dd HH:mm"));''',
    "split_string": r'''
string[] parts = "a,b,c".Split(',');
Console.WriteLine(string.Join("-", parts)); // a-b-c''',
    "sum_max": r'''
int[] nums = { 4, 8, 15 };
Console.WriteLine($"{nums.Sum()} {nums.Max()} {nums.Min()}"); // 27 15 4''',
}
