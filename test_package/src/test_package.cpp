#include <cstddef>
#include <string_view>

#if defined(_LIBCPP_VERSION)
constexpr std::string_view standard_library = "libc++";
#else
constexpr std::string_view standard_library = "unknown";
#endif

int main()
{
    return standard_library == "libc++" ? 0 : 1;
}