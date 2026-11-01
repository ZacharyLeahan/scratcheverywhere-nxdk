#pragma once
#include <algorithm>
#include <cctype>
#include <string>
#include <unordered_map>
#include <vector>

struct Block;

// A sprite's authored hats are immutable after parsing. Clones share the
// original's index, while each dispatch still starts a thread on every clone.
class BroadcastHatIndex {
    bool ready = false;
    std::unordered_map<std::string, std::vector<Block *>> listeners;

  public:
    template <class Hats, class Name>
    const std::vector<Block *> &lookup(const std::string &normalized, const Hats &hats, Name name) {
        if (!ready) {
            for (Block *hat : hats) {
                std::string key = name(hat);
                std::transform(key.begin(), key.end(), key.begin(), [](unsigned char c) { return std::tolower(c); });
                listeners[key].push_back(hat);
            }
            ready = true;
        }
        auto found = listeners.find(normalized);
        static const std::vector<Block *> empty;
        return found == listeners.end() ? empty : found->second;
    }
};
