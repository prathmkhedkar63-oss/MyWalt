#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <algorithm>
#include <chrono>
#include <cctype>
#include <fstream>
#include <sstream>

#if defined(_WIN32)
#include <windows.h>
#include <shellapi.h>
#endif

namespace fs = std::filesystem;

// --- JSON Escaping ---
static std::string esc_json(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 16);
    for (char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 32) {
                    char buf[8];
                    snprintf(buf, sizeof(buf), "\\u%04x", static_cast<unsigned char>(c));
                    out += buf;
                } else {
                    out += c;
                }
                break;
        }
    }
    return out;
}

static bool contains_ci(const std::string& haystack, const std::string& needle) {
    if (needle.empty()) return true;
    auto it = std::search(
        haystack.begin(), haystack.end(),
        needle.begin(), needle.end(),
        [](char a, char b) {
            return std::tolower(static_cast<unsigned char>(a)) ==
                   std::tolower(static_cast<unsigned char>(b));
        }
    );
    return it != haystack.end();
}

static uint64_t file_time_to_epoch(const fs::file_time_type& ft) {
    try {
        auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
            ft - fs::file_time_type::clock::now() + std::chrono::system_clock::now()
        );
        return std::chrono::duration_cast<std::chrono::seconds>(sctp.time_since_epoch()).count();
    } catch (...) {
        return 0;
    }
}

// ============================================================================
// 1. DIRECTORY LISTING
// ============================================================================
static int cmd_list(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "{\"error\": \"Usage: native_engine list <directory> [show_hidden: 0|1]\"}\n";
        return 1;
    }

    std::string dir_path = argv[2];
    bool show_hidden = (argc >= 4 && std::string(argv[3]) == "1");

    auto start = std::chrono::high_resolution_clock::now();
    fs::path p(dir_path);
    std::error_code ec;

    if (!fs::exists(p, ec) || !fs::is_directory(p, ec)) {
        std::cout << "{\"error\": \"Directory not found or not accessible\", \"items\": []}\n";
        return 1;
    }

    struct Item {
        std::string name;
        std::string path;
        bool is_dir;
        uintmax_t size;
        uint64_t modified;
    };

    std::vector<Item> items;
    fs::directory_iterator it(p, fs::directory_options::skip_permission_denied, ec);
    fs::directory_iterator end;

    while (it != end && !ec) {
        try {
            const auto& entry = *it;
            std::string fname = entry.path().filename().string();
            if (!show_hidden && !fname.empty() && fname[0] == '.') {
                it.increment(ec);
                if (ec) ec.clear();
                continue;
            }

            Item item;
            item.name = fname;
            item.path = entry.path().string();
            item.is_dir = entry.is_directory(ec);
            item.size = (!item.is_dir && !ec) ? entry.file_size(ec) : 0;
            auto ftime = entry.last_write_time(ec);
            item.modified = ec ? 0 : file_time_to_epoch(ftime);

            items.push_back(item);
        } catch (...) {}

        it.increment(ec);
        if (ec) ec.clear();
    }

    // Sort: directories first, then alphabetical case-insensitive
    std::sort(items.begin(), items.end(), [](const Item& a, const Item& b) {
        if (a.is_dir != b.is_dir) return a.is_dir > b.is_dir;
        std::string la = a.name, lb = b.name;
        std::transform(la.begin(), la.end(), la.begin(), ::tolower);
        std::transform(lb.begin(), lb.end(), lb.begin(), ::tolower);
        return la < lb;
    });

    auto end_time = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(end_time - start).count();

    std::cout << "{\n";
    std::cout << "  \"directory\": \"" << esc_json(dir_path) << "\",\n";
    std::cout << "  \"duration_ms\": " << ms << ",\n";
    std::cout << "  \"count\": " << items.size() << ",\n";
    std::cout << "  \"items\": [\n";

    for (size_t i = 0; i < items.size(); ++i) {
        const auto& itm = items[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << esc_json(itm.name) << "\",\n";
        std::cout << "      \"path\": \"" << esc_json(itm.path) << "\",\n";
        std::cout << "      \"is_dir\": " << (itm.is_dir ? "true" : "false") << ",\n";
        std::cout << "      \"size\": " << itm.size << ",\n";
        std::cout << "      \"modified\": " << itm.modified << "\n";
        std::cout << "    }" << (i + 1 < items.size() ? "," : "") << "\n";
    }

    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}

// ============================================================================
// 2. RECURSIVE DISK SPACE ANALYZER
// ============================================================================
struct FileInfo {
    std::string path;
    std::string name;
    uintmax_t size;
};

static int cmd_analyze(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "{\"error\": \"Usage: native_engine analyze <directory>\"}\n";
        return 1;
    }

    std::string dir_path = argv[2];
    auto start = std::chrono::high_resolution_clock::now();
    fs::path root(dir_path);
    std::error_code ec;

    if (!fs::exists(root, ec) || !fs::is_directory(root, ec)) {
        std::cout << "{\"error\": \"Invalid target directory\"}\n";
        return 1;
    }

    struct FolderInfo {
        std::string name;
        std::string path;
        uintmax_t size = 0;
        size_t file_count = 0;
    };

    std::vector<FolderInfo> subfolders;
    std::vector<FileInfo> direct_files;
    std::vector<FileInfo> all_large_files;
    uintmax_t total_size = 0;
    size_t total_files = 0;
    size_t total_dirs = 0;

    // Scan top-level entries first
    fs::directory_iterator top_it(root, fs::directory_options::skip_permission_denied, ec);
    fs::directory_iterator end_dir;

    std::vector<fs::directory_entry> entries;
    while (top_it != end_dir && !ec) {
        entries.push_back(*top_it);
        top_it.increment(ec);
        if (ec) ec.clear();
    }

    for (const auto& entry : entries) {
        std::string fname = entry.path().filename().string();
        if (entry.is_directory(ec)) {
            FolderInfo f;
            f.name = fname;
            f.path = entry.path().string();
            total_dirs++;

            // Recursively calculate subfolder size
            fs::recursive_directory_iterator sub_it(entry.path(), fs::directory_options::skip_permission_denied, ec);
            fs::recursive_directory_iterator sub_end;
            while (sub_it != sub_end && !ec) {
                try {
                    const auto& sub_entry = *sub_it;
                    if (sub_entry.is_directory(ec)) {
                        total_dirs++;
                    } else if (sub_entry.is_regular_file(ec)) {
                        uintmax_t fsize = sub_entry.file_size(ec);
                        if (!ec) {
                            f.size += fsize;
                            f.file_count++;
                            total_size += fsize;
                            total_files++;

                            if (fsize > 1024 * 1024) { // Files > 1MB eligible for top largest
                                all_large_files.push_back({sub_entry.path().string(), sub_entry.path().filename().string(), fsize});
                            }
                        }
                    }
                } catch (...) {}
                sub_it.increment(ec);
                if (ec) ec.clear();
            }
            subfolders.push_back(f);
        } else if (entry.is_regular_file(ec)) {
            uintmax_t fsize = entry.file_size(ec);
            if (!ec) {
                total_size += fsize;
                total_files++;
                direct_files.push_back({entry.path().string(), fname, fsize});
                all_large_files.push_back({entry.path().string(), fname, fsize});
            }
        }
    }

    // Sort subfolders by size descending
    std::sort(subfolders.begin(), subfolders.end(), [](const FolderInfo& a, const FolderInfo& b) {
        return a.size > b.size;
    });

    // Sort largest files descending, take top 20
    std::sort(all_large_files.begin(), all_large_files.end(), [](const FileInfo& a, const FileInfo& b) {
        return a.size > b.size;
    });
    if (all_large_files.size() > 20) {
        all_large_files.resize(20);
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(end_time - start).count();

    std::cout << "{\n";
    std::cout << "  \"root\": \"" << esc_json(dir_path) << "\",\n";
    std::cout << "  \"duration_ms\": " << ms << ",\n";
    std::cout << "  \"total_size\": " << total_size << ",\n";
    std::cout << "  \"total_files\": " << total_files << ",\n";
    std::cout << "  \"total_dirs\": " << total_dirs << ",\n";
    std::cout << "  \"subfolders\": [\n";

    for (size_t i = 0; i < subfolders.size(); ++i) {
        const auto& f = subfolders[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << esc_json(f.name) << "\",\n";
        std::cout << "      \"path\": \"" << esc_json(f.path) << "\",\n";
        std::cout << "      \"size\": " << f.size << ",\n";
        std::cout << "      \"file_count\": " << f.file_count << "\n";
        std::cout << "    }" << (i + 1 < subfolders.size() ? "," : "") << "\n";
    }

    std::cout << "  ],\n";
    std::cout << "  \"largest_files\": [\n";

    for (size_t i = 0; i < all_large_files.size(); ++i) {
        const auto& lf = all_large_files[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << esc_json(lf.name) << "\",\n";
        std::cout << "      \"path\": \"" << esc_json(lf.path) << "\",\n";
        std::cout << "      \"size\": " << lf.size << "\n";
        std::cout << "    }" << (i + 1 < all_large_files.size() ? "," : "") << "\n";
    }

    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}

// ============================================================================
// 3. FAST FILENAME & FULLTEXT SEARCH
// ============================================================================
static int cmd_search(int argc, char* argv[]) {
    if (argc < 4) {
        std::cout << "{\"error\": \"Usage: native_engine search <directory> <query> [max]\"}\n";
        return 1;
    }

    std::string dir_path = argv[2];
    std::string query = argv[3];
    size_t max_results = 100;
    if (argc >= 5) {
        try { max_results = std::stoul(argv[4]); } catch (...) {}
    }

    auto start = std::chrono::high_resolution_clock::now();
    fs::path root(dir_path);
    std::error_code ec;

    struct SearchItem {
        std::string name;
        std::string path;
        bool is_dir;
        uintmax_t size;
    };

    std::vector<SearchItem> results;

    if (fs::exists(root, ec)) {
        fs::recursive_directory_iterator it(root, fs::directory_options::skip_permission_denied, ec);
        fs::recursive_directory_iterator end;

        while (it != end && !ec) {
            if (results.size() >= max_results) break;
            try {
                const auto& entry = *it;
                std::string fname = entry.path().filename().string();
                if (contains_ci(fname, query)) {
                    SearchItem si;
                    si.name = fname;
                    si.path = entry.path().string();
                    si.is_dir = entry.is_directory(ec);
                    si.size = (!si.is_dir && !ec) ? entry.file_size(ec) : 0;
                    results.push_back(si);
                }
            } catch (...) {}
            it.increment(ec);
            if (ec) ec.clear();
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(end_time - start).count();

    std::cout << "{\n";
    std::cout << "  \"query\": \"" << esc_json(query) << "\",\n";
    std::cout << "  \"root\": \"" << esc_json(dir_path) << "\",\n";
    std::cout << "  \"duration_ms\": " << ms << ",\n";
    std::cout << "  \"count\": " << results.size() << ",\n";
    std::cout << "  \"results\": [\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        std::cout << "    {\n";
        std::cout << "      \"name\": \"" << esc_json(r.name) << "\",\n";
        std::cout << "      \"path\": \"" << esc_json(r.path) << "\",\n";
        std::cout << "      \"is_dir\": " << (r.is_dir ? "true" : "false") << ",\n";
        std::cout << "      \"size\": " << r.size << "\n";
        std::cout << "    }" << (i + 1 < results.size() ? "," : "") << "\n";
    }

    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}

// ============================================================================
// 4. BATCH FILE MUTATION OPERATIONS (DELETE / COPY / MOVE)
// ============================================================================
static int cmd_batch_delete(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "{\"error\": \"Usage: native_engine batch_delete <path1> [path2 ...]\"}\n";
        return 1;
    }

    std::vector<std::string> deleted;
    std::vector<std::pair<std::string, std::string>> failed;

    for (int i = 2; i < argc; ++i) {
        std::string p_str = argv[i];
        std::error_code ec;
        fs::path p(p_str);

        if (!fs::exists(p, ec)) {
            failed.push_back({p_str, "File or folder does not exist"});
            continue;
        }

#if defined(_WIN32)
        // Soft-delete to Windows Recycle Bin via Win32 SHFileOperation
        SHFILEOPSTRUCTW fileop = {0};
        std::wstring wp(p_str.begin(), p_str.end());
        wp.push_back(L'\0');
        wp.push_back(L'\0');

        fileop.wFunc = FO_DELETE;
        fileop.pFrom = wp.c_str();
        fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT;

        int res = SHFileOperationW(&fileop);
        if (res == 0 && !fileop.fAnyOperationsAborted) {
            deleted.push_back(p_str);
            continue;
        }
#endif

        // Permanent delete fallback
        if (fs::is_directory(p, ec)) {
            fs::remove_all(p, ec);
        } else {
            fs::remove(p, ec);
        }

        if (ec) {
            failed.push_back({p_str, ec.message()});
        } else {
            deleted.push_back(p_str);
        }
    }

    std::cout << "{\n";
    std::cout << "  \"deleted\": [\n";
    for (size_t i = 0; i < deleted.size(); ++i) {
        std::cout << "    \"" << esc_json(deleted[i]) << "\"" << (i + 1 < deleted.size() ? "," : "") << "\n";
    }
    std::cout << "  ],\n";
    std::cout << "  \"failed\": [\n";
    for (size_t i = 0; i < failed.size(); ++i) {
        std::cout << "    {\"path\": \"" << esc_json(failed[i].first) << "\", \"error\": \"" << esc_json(failed[i].second) << "\"}"
                  << (i + 1 < failed.size() ? "," : "") << "\n";
    }
    std::cout << "  ]\n";
    std::cout << "}\n";
    return 0;
}

// ============================================================================
// MAIN ENTRY POINT / DISPATCHER
// ============================================================================
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "{\n";
        std::cout << "  \"engine\": \"MyWalt C++ Native File Engine\",\n";
        std::cout << "  \"version\": \"2.0.0\",\n";
        std::cout << "  \"commands\": [\"list\", \"analyze\", \"search\", \"batch_delete\"]\n";
        std::cout << "}\n";
        return 0;
    }

    std::string cmd = argv[1];
    if (cmd == "list") {
        return cmd_list(argc, argv);
    } else if (cmd == "analyze") {
        return cmd_analyze(argc, argv);
    } else if (cmd == "search") {
        return cmd_search(argc, argv);
    } else if (cmd == "batch_delete") {
        return cmd_batch_delete(argc, argv);
    } else {
        std::cout << "{\"error\": \"Unknown command: " << esc_json(cmd) << "\"}\n";
        return 1;
    }
}
