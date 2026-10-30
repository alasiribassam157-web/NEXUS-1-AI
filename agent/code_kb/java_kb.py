"""Java snippets (Java 11+). Statements go inside main() unless they declare a class or method."""

SNIPPETS = {
    "hello_world": r'''
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}''',
    "variables": r'''
String name = "Sara";
int age = 25;
double pi = 3.14;
boolean isActive = true;
System.out.println(name + " " + age + " " + pi + " " + isActive);''',
    "if_else": r'''
int age = 20;
if (age >= 18) {
    System.out.println("Adult");
} else if (age >= 13) {
    System.out.println("Teen");
} else {
    System.out.println("Child");
}''',
    "for_loop": r'''
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

for (String fruit : new String[] {"apple", "banana"}) {
    System.out.println(fruit);
}''',
    "while_loop": r'''
int count = 0;
while (count < 5) {
    System.out.println(count);
    count++;
}''',
    "function": r'''
static int add(int a, int b) {
    return a + b;
}

// inside main:
System.out.println(add(2, 3)); // 5''',
    "list": r'''
import java.util.ArrayList;
import java.util.List;

List<Integer> nums = new ArrayList<>(List.of(3, 1, 2));
nums.add(4);
System.out.println(nums.get(0) + " " + nums.size()); // 3 4''',
    "dict": r'''
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> ages = new HashMap<>();
ages.put("Ali", 30);
ages.put("Sara", 25);
for (Map.Entry<String, Integer> e : ages.entrySet()) {
    System.out.println(e.getKey() + " " + e.getValue());
}''',
    "class": r'''
class Person {
    private final String name;

    Person(String name) {
        this.name = name;
    }

    String greet() {
        return "Hi, I'm " + name;
    }
}

// inside main:
System.out.println(new Person("Ali").greet());''',
    "read_file": r'''
import java.nio.file.Files;
import java.nio.file.Path;

String content = Files.readString(Path.of("data.txt")); // throws IOException
System.out.println(content);''',
    "write_file": r'''
import java.nio.file.Files;
import java.nio.file.Path;

Files.writeString(Path.of("out.txt"), "Hello file\n"); // throws IOException''',
    "reverse_string": r'''
String reversed = new StringBuilder("hello").reverse().toString();
System.out.println(reversed); // olleh''',
    "sort_list": r'''
import java.util.Arrays;

int[] nums = {5, 2, 9, 1};
Arrays.sort(nums);
System.out.println(Arrays.toString(nums)); // [1, 2, 5, 9]''',
    "try_catch": r'''
try {
    int x = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Error: " + e.getMessage());
} finally {
    System.out.println("done");
}''',
    "http_request": r'''
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder(URI.create("https://api.github.com")).build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.statusCode());''',
    "json_parse": r'''
// Java has no built-in JSON parser; the usual choice is Jackson (jackson-databind).
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

JsonNode data = new ObjectMapper().readTree("{\"name\": \"Ali\", \"age\": 30}");
System.out.println(data.get("name").asText()); // Ali''',
    "random_number": r'''
import java.util.Random;

int n = new Random().nextInt(100) + 1; // 1..100
System.out.println(n);''',
    "current_date": r'''
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"));
System.out.println(now);''',
    "split_string": r'''
String[] parts = "a,b,c".split(",");
System.out.println(String.join("-", parts)); // a-b-c''',
    "sum_max": r'''
import java.util.Arrays;

int[] nums = {4, 8, 15};
System.out.println(Arrays.stream(nums).sum());              // 27
System.out.println(Arrays.stream(nums).max().getAsInt());   // 15''',
}
