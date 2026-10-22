import std;

#include <gtest/gtest.h>

static std::vector<int> static_initializer_probe(128, 7);

static auto foo() -> int
{
    std::println("Hello world!");

    const std::regex expression{"test_regex"};

    std::unordered_map<std::string, int> counts;
    counts["Test"] = 1;

    return
        (std::regex_match("test_regex", expression)
        && static_initializer_probe.size() == 128) ? 0 : 1;
}

TEST(TEST, RunTestFunction)
{
    ASSERT_EQ(foo(), 0);
}