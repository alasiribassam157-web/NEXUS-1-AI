"""Go snippets. Statements go inside func main() with the listed imports."""

SNIPPETS = {
    "hello_world": r'''
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}''',
    "variables": r'''
name := "Sara"
age := 25
pi := 3.14
isActive := true
fmt.Println(name, age, pi, isActive)''',
    "if_else": r'''
age := 20
if age >= 18 {
    fmt.Println("Adult")
} else if age >= 13 {
    fmt.Println("Teen")
} else {
    fmt.Println("Child")
}''',
    "for_loop": r'''
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

for _, fruit := range []string{"apple", "banana"} {
    fmt.Println(fruit)
}''',
    "while_loop": r'''
count := 0
for count < 5 { // Go uses "for" as its while loop
    fmt.Println(count)
    count++
}''',
    "function": r'''
func add(a, b int) int {
    return a + b
}

// inside main:
fmt.Println(add(2, 3)) // 5''',
    "list": r'''
nums := []int{3, 1, 2}
nums = append(nums, 4)
fmt.Println(nums[0], len(nums)) // 3 4''',
    "dict": r'''
ages := map[string]int{"Ali": 30, "Sara": 25}
ages["Omar"] = 22
for name, age := range ages {
    fmt.Println(name, age)
}''',
    "class": r'''
type Person struct {
    Name string
}

func (p Person) Greet() string {
    return "Hi, I'm " + p.Name
}

// inside main:
fmt.Println(Person{Name: "Ali"}.Greet())''',
    "read_file": r'''
// import "os", "log"
data, err := os.ReadFile("data.txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data))''',
    "write_file": r'''
// import "os", "log"
err := os.WriteFile("out.txt", []byte("Hello file\n"), 0644)
if err != nil {
    log.Fatal(err)
}''',
    "reverse_string": r'''
func reverse(s string) string {
    r := []rune(s)
    for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
        r[i], r[j] = r[j], r[i]
    }
    return string(r)
}

// reverse("hello") == "olleh"''',
    "sort_list": r'''
// import "sort"
nums := []int{5, 2, 9, 1}
sort.Ints(nums)
fmt.Println(nums) // [1 2 5 9]''',
    "try_catch": r'''
// Go has no exceptions: functions return an error value. import "strconv"
n, err := strconv.Atoi("abc")
if err != nil {
    fmt.Println("Error:", err)
    return
}
fmt.Println(n)''',
    "http_request": r'''
// import "io", "log", "net/http"
resp, err := http.Get("https://api.github.com")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)
fmt.Println(resp.StatusCode, len(body))''',
    "json_parse": r'''
// import "encoding/json", "log"
var data map[string]any
if err := json.Unmarshal([]byte(`{"name": "Ali", "age": 30}`), &data); err != nil {
    log.Fatal(err)
}
fmt.Println(data["name"]) // Ali''',
    "random_number": r'''
// import "math/rand"
n := rand.Intn(100) + 1 // 1..100
fmt.Println(n)''',
    "current_date": r'''
// import "time"
fmt.Println(time.Now().Format("2006-01-02 15:04"))''',
    "split_string": r'''
// import "strings"
parts := strings.Split("a,b,c", ",")
fmt.Println(parts)                    // [a b c]
fmt.Println(strings.Join(parts, "-")) // a-b-c''',
    "sum_max": r'''
nums := []int{4, 8, 15}
sum, mx := 0, nums[0]
for _, n := range nums {
    sum += n
    if n > mx {
        mx = n
    }
}
fmt.Println(sum, mx) // 27 15''',
}
