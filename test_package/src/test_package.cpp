// #include <regex>
// #include <string_view>
// #include <vector>
import std;

#if defined(_LIBCPP_VERSION)
constexpr std::string_view standard_library = "libc++";
#else
constexpr std::string_view standard_library = "unknown";
#endif

static std::vector<int> static_initializer_probe(128, 7);

int main()
{
    const std::regex expression{"test_regex"};

    return
        (standard_library == "libc++"
        && std::regex_match("test_regex", expression)
        && static_initializer_probe.size() == 128) ? 0 : 1;
}