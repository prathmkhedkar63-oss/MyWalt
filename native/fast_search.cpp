#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <algorithm>
#include <chrono>
#include <cctype>

namespace fs = std::filesystem;

struct SearchResult {
    std::string path;
    std::string filename;
    uintmax_t size;
    bool is_directory;
};

static bool contains_ci(const std::string& str, const std::string& q) {
    if (q.empty()) return true;
    auto it = std::search(
        str.begin(), str.end(),
        q.begin(), q.end(),
        [](char a, char b) {
            return std::tolower(static_cast<unsigned char>(a)) ==
                   std::tolower(static_cast<unsigned char>(b));
        }
    );
    return it != str.end();
}

static std::string esc_json(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 16);
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else if (c == '\r') out += "\\r";
        else if (c == '\t') out += "\\t";
        else if (static_cast<unsigned char>(c) < 32) out += " ";
        else out += c;
    }
    return out;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "{\"error\": \"Usage: fast_search <root_path> <query> [max]\", \"results\": []}\n";
        return 1;
    }

    std::string root_path = argv[1];
    std::string query = argv[2];
    size_t max_results = 100;
    if (argc >= 4) {
        try { max_results = std::stoul(argv[3]); } catch (...) {}
    }

    std::vector<SearchResult> results;
    auto start = std::chrono::high_resolution_clock::now();

    try {
        fs::path p(root_path);
        if (fs::exists(p)) {
            std::error_code ec;
            fs::recursive_directory_iterator it(p, fs::directory_options::skip_permission_denied, ec);
            fs::recursive_directory_iterator end;

            while (it != end && !ec) {
                if (results.size() >= max_results) break;
                try {
                    const auto& entry = *it;
                    std::string fname = entry.path().filename().string();
                    if (contains_ci(fname, query)) {
                        SearchResult sr;
                        sr.path = entry.path().string();
                        sr.filename = fname;
                        sr.is_directory = entry.is_directory(ec);
                        sr.size = (!sr.is_directory && !ec) ? entry.file_size(ec) : 0;
                        results.push_back(sr);
                    }
                } catch (...) {}
                it.increment(ec);
                if (ec) ec.clear();
            }
        }
    } catch (...) {}

    auto end = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(end - start).count();

    std::cout << "{\n";
    std::cout << "  \"query\": \"" << esc_json(query) << "\",\n";
    std::cout << "  \"root\": \"" << esc_json(root_path) << "\",\n";
    std::cout << "  \"duration_ms\": " << ms << ",\n";
    std::cout << "  \"count\": " << results.size() << ",\n";
    std::cout << "  \"results\": [\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << esc_json(r.filename) << "\",\n";
        std::cout << "      \"path\": \"" << esc_json(r.path) << "\",\n";
        std::cout << "      \"is_dir\": " << (r.is_directory ? "true" : "false") << ",\n";
        std::cout << "      \"size\": " << r.size << "\n";
        std::cout << "    }" << (i + 1 < results.size() ? "," : "") << "\n";
    }

    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}
