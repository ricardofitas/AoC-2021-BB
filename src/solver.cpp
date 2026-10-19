// Exact, memory-conscious solvers for the synthetic AoC 2021 Big Inputs.
#include <algorithm>
#include <array>
#include <bit>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;
using i64 = int64_t;
using u64 = uint64_t;
using u128 = __uint128_t;

string decimal(u128 n) {
    if (!n)
        return "0";
    string s;
    while (n) {
        s += char('0' + n % 10);
        n /= 10;
    }
    reverse(s.begin(), s.end());
    return s;
}
void output(u128 a, u128 b) {
    cout << decimal(a) << '\n' << decimal(b) << '\n';
}
vector<i64> parse_numbers(string s) {
    for (size_t i = 0; i < s.size(); ++i)
        if (!isdigit(static_cast<unsigned char>(s[i])) &&
            !(s[i] == '-' && i + 1 < s.size() && isdigit(static_cast<unsigned char>(s[i + 1]))))
            s[i] = ' ';
    istringstream in(s);
    vector<i64> out;
    i64 x;
    while (in >> x)
        out.push_back(x);
    return out;
}
struct Grid {
    size_t h, w;
    vector<uint8_t> a;
};
Grid grid(istream &in) {
    Grid g{0, 0, {}};
    string line;
    while (getline(in, line)) {
        if (!line.empty() && line.back() == '\r')
            line.pop_back();
        if (line.empty())
            continue;
        if (!g.w)
            g.w = line.size();
        if (line.size() != g.w)
            throw runtime_error("Ragged grid");
        for (char c : line) {
            if (c < '0' || c > '9')
                throw runtime_error("Non-digit grid cell");
            g.a.push_back(c - '0');
        }
        ++g.h;
    }
    if (!g.h)
        throw runtime_error("Empty grid");
    return g;
}

void bingo(istream &in) {
    string line;
    getline(in, line);
    auto draws = parse_numbers(line);
    unordered_map<i64, size_t> time;
    for (size_t i = 0; i < draws.size(); ++i)
        time.emplace(draws[i], i);
    size_t first = numeric_limits<size_t>::max(), last = 0;
    u128 p1 = 0, p2 = 0;
    bool found = false;
    vector<vector<i64>> board;
    auto finish = [&]() {
        if (board.empty())
            return;
        size_t n = board.size();
        for (auto &row : board)
            if (row.size() != n)
                throw runtime_error("Bingo boards must be square");
        const size_t never = draws.size();
        vector<size_t> rows(n), cols(n);
        for (size_t y = 0; y < n; ++y)
            for (size_t x = 0; x < n; ++x) {
                auto it = time.find(board[y][x]);
                size_t t = it == time.end() ? never : it->second;
                rows[y] = max(rows[y], t);
                cols[x] = max(cols[x], t);
            }
        size_t win =
            min(*min_element(rows.begin(), rows.end()), *min_element(cols.begin(), cols.end()));
        if (win != never) {
            u128 sum = 0;
            for (auto &row : board)
                for (i64 v : row) {
                    if (v < 0)
                        throw runtime_error("Negative bingo cell");
                    auto it = time.find(v);
                    if (it == time.end() || it->second > win)
                        sum += v;
                }
            u128 score = sum * draws[win];
            if (win < first) {
                first = win;
                p1 = score;
            }
            // Input order breaks simultaneous last-win ties deterministically.
            if (!found || win >= last) {
                last = win;
                p2 = score;
            }
            found = true;
        }
        board.clear();
    };
    while (getline(in, line)) {
        auto row = parse_numbers(line);
        if (row.empty())
            finish();
        else
            board.push_back(move(row));
    }
    finish();
    if (!found)
        throw runtime_error("No winning board");
    output(p1, p2);
}

struct Vent {
    i64 x, y, u, v;
    int o;
};
struct Segment {
    i64 b, l, r;
    uint8_t doubled;
};
vector<Segment> merge_lines(const vector<Vent> &vents, int orientation) {
    map<i64, vector<pair<i64, int>>> lines;
    for (auto s : vents)
        if (s.o == orientation) {
            i64 b = orientation == 0   ? s.y
                    : orientation == 1 ? s.x
                    : orientation == 2 ? s.y - s.x
                                       : s.y + s.x;
            i64 l = orientation == 1 ? min(s.y, s.v) : min(s.x, s.u);
            i64 r = orientation == 1 ? max(s.y, s.v) : max(s.x, s.u);
            lines[b].push_back({l, 1});
            lines[b].push_back({r + 1, -1});
        }
    vector<Segment> result;
    for (auto &[b, events] : lines) {
        sort(events.begin(), events.end());
        int count = 0;
        i64 previous = events.front().first;
        for (size_t i = 0; i < events.size();) {
            i64 x = events[i].first;
            if (count && previous < x) {
                uint8_t doubled = count >= 2 ? uint8_t(1 << orientation) : 0;
                if (!result.empty() && result.back().b == b && result.back().r + 1 == previous &&
                    result.back().doubled == doubled)
                    result.back().r = x - 1;
                else
                    result.push_back({b, previous, x - 1, doubled});
            }
            while (i < events.size() && events[i].first == x)
                count += events[i++].second;
            previous = x;
        }
    }
    return result;
}
void vents(istream &in) {
    vector<Vent> all;
    string line;
    i64 xmax = 0, ymax = 0;
    while (getline(in, line)) {
        if (line.empty())
            continue;
        auto n = parse_numbers(line);
        if (n.size() != 4)
            throw runtime_error("Invalid vent");
        auto [x, y, u, v] = tuple{n[0], n[1], n[2], n[3]};
        if (min({x, y, u, v}) < 0 || max({x, y, u, v}) >= (i64(1) << 30))
            throw runtime_error("Vent coordinates must be in [0, 2^30)");
        int o = y == v ? 0 : x == u ? 1 : (v - y) == (u - x) ? 2 : (v - y) == -(u - x) ? 3 : -1;
        if (o < 0)
            throw runtime_error("Only horizontal, vertical and 45-degree vents are supported");
        all.push_back({x, y, u, v, o});
        xmax = max({xmax, x, u});
        ymax = max({ymax, y, v});
    }
    if (all.empty())
        throw runtime_error("No vents");
    // Small domains: saturating byte counts are much faster than an intersection sweep.
    if (u64(xmax + 1) * u64(ymax + 1) <= 100000000) {
        size_t w = xmax + 1;
        vector<uint8_t> cells(w * (ymax + 1));
        auto add = [&](Vent s) {
            i64 dx = (s.u > s.x) - (s.u < s.x), dy = (s.v > s.y) - (s.v < s.y);
            i64 len = max(abs(s.u - s.x), abs(s.v - s.y));
            i64 index = s.y * i64(w) + s.x, step = dy * i64(w) + dx;
            for (i64 i = 0; i <= len; ++i, index += step)
                if (cells[index] < 2)
                    ++cells[index];
        };
        for (auto s : all)
            if (s.o < 2)
                add(s);
        u64 p1 = count(cells.begin(), cells.end(), uint8_t(2));
        for (auto s : all)
            if (s.o >= 2)
                add(s);
        output(p1, count(cells.begin(), cells.end(), uint8_t(2)));
        return;
    }
    array<vector<Segment>, 4> groups;
    i64 base = 0;
    vector<u64> intersections;
    unsigned bits =
        bit_width(u64(max(xmax, ymax))); // Two coordinates and a 4-bit mask fit in 64 bits.
    auto correct = [&](i64 total) {
        sort(intersections.begin(), intersections.end());
        for (size_t i = 0; i < intersections.size();) {
            u64 key = intersections[i] >> 4, mask = 0;
            do {
                mask |= intersections[i++] & 15;
            } while (i < intersections.size() && (intersections[i] >> 4) == key);
            total += 1 - popcount(mask);
        }
        return total;
    };
    i64 p1 = 0;
    for (int b = 0; b < 4; ++b) {
        groups[b] = merge_lines(all, b);
        for (auto s : groups[b])
            if (s.doubled)
                base += s.r - s.l + 1;
        for (int a = 0; a < b; ++a)
            for (auto s : groups[a])
                for (auto t : groups[b]) {
                    i64 x, y;
                    if (a == 0) {
                        y = s.b;
                        x = b == 1 ? t.b : b == 2 ? y - t.b : t.b - y;
                    } else if (a == 1) {
                        x = s.b;
                        y = b == 2 ? x + t.b : t.b - x;
                    } else {
                        i64 delta = t.b - s.b;
                        if (delta % 2)
                            continue;
                        x = delta / 2;
                        y = x + s.b;
                    }
                    i64 p = a == 1 ? y : x, q = b == 1 ? y : x;
                    if (p < s.l || p > s.r || q < t.l || q > t.r)
                        continue;
                    u64 key = (u64(x) << bits) | u64(y);
                    intersections.push_back((key << 4) | s.doubled | t.doubled);
                }
        if (b == 1)
            p1 = correct(base);
    }
    output(p1, correct(base));
}

void basins(istream &in) {
    auto g = grid(in);
    auto &a = g.a;
    u64 risk = 0;
    for (size_t y = 0; y < g.h; ++y)
        for (size_t x = 0; x < g.w; ++x) {
            size_t i = y * g.w + x;
            uint8_t v = a[i];
            if ((!x || v < a[i - 1]) && (x + 1 == g.w || v < a[i + 1]) && (!y || v < a[i - g.w]) &&
                (y + 1 == g.h || v < a[i + g.w]))
                risk += v + 1;
        }
    array<u64, 3> top{};
    vector<size_t> queue;
    for (size_t start = 0; start < a.size(); ++start)
        if (a[start] < 9) {
            queue.clear();
            queue.push_back(start);
            a[start] = 9;
            for (size_t p = 0; p < queue.size(); ++p) {
                size_t i = queue[p], x = i % g.w;
                auto add = [&](size_t j) {
                    if (a[j] < 9) {
                        a[j] = 9;
                        queue.push_back(j);
                    }
                };
                if (x)
                    add(i - 1);
                if (x + 1 < g.w)
                    add(i + 1);
                if (i >= g.w)
                    add(i - g.w);
                if (i + g.w < a.size())
                    add(i + g.w);
            }
            if (queue.size() > top[0]) {
                top[0] = queue.size();
                sort(top.begin(), top.end());
            }
        }
    output(risk, u128(top[0]) * top[1] * top[2]);
}
void octopi(istream &in) {
    auto g = grid(in);
    size_t stride = g.w + 2;
    vector<uint8_t> a((g.h + 2) * stride, 255);
    vector<size_t> queue;
    queue.reserve(g.a.size());
    for (size_t y = 0; y < g.h; ++y)
        copy_n(g.a.begin() + y * g.w, g.w, a.begin() + (y + 1) * stride + 1);
    array<ptrdiff_t, 8> deltas = {
        -ptrdiff_t(stride) - 1, -ptrdiff_t(stride), -ptrdiff_t(stride) + 1, -1, 1,
        ptrdiff_t(stride) - 1,  ptrdiff_t(stride),  ptrdiff_t(stride) + 1};
    u64 p1 = 0, p2 = 0;
    for (u64 step = 1; step <= 1000000; ++step) {
        queue.clear();
        for (size_t y = 1; y <= g.h; ++y)
            for (size_t x = 1; x <= g.w; ++x) {
                size_t i = y * stride + x;
                if (++a[i] == 10)
                    queue.push_back(i);
            }
        for (size_t p = 0; p < queue.size(); ++p) {
            size_t i = queue[p];
            a[i] = 0;
            for (ptrdiff_t d : deltas) {
                size_t j = i + d;
                if (a[j] != 255 && a[j] != 0 && ++a[j] == 10)
                    queue.push_back(j);
            }
        }
        if (step <= 100)
            p1 += queue.size();
        if (!p2 && queue.size() == g.a.size())
            p2 = step;
        if (step >= 100 && p2) {
            output(p1, p2);
            return;
        }
    }
    throw runtime_error("No synchronization within 1,000,000 steps");
}

struct Counts {
    u128 once = 0, twice = 0;
};
void caves(istream &in) {
    map<string, int> ids;
    vector<string> names;
    vector<pair<int, int>> edges;
    string line;
    auto id = [&](const string &s) {
        auto [it, added] = ids.emplace(s, ids.size());
        if (added)
            names.push_back(s);
        return it->second;
    };
    while (getline(in, line)) {
        if (!line.empty() && line.back() == '\r')
            line.pop_back();
        if (line.empty())
            continue;
        auto dash = line.find('-');
        if (dash == string::npos)
            throw runtime_error("Invalid cave edge");
        int a = id(line.substr(0, dash)), b = id(line.substr(dash + 1));
        edges.push_back({a, b});
    }
    if (!ids.count("start") || !ids.count("end"))
        throw runtime_error("Missing start/end");
    int start = ids.at("start"), end = ids.at("end"), n = 0;
    vector<int> small(names.size(), -1);
    vector<bool> big(names.size());
    for (size_t i = 0; i < names.size(); ++i) {
        big[i] =
            all_of(names[i].begin(), names[i].end(), [](unsigned char c) { return isupper(c); });
        if (!big[i] && int(i) != start && int(i) != end)
            small[i] = n++;
    }
    if (n > 24)
        throw runtime_error("Layered cave solver supports at most 24 ordinary small caves");
    small[start] = n;
    small[end] = n + 1;
    vector<vector<int>> adjacency(names.size());
    for (auto [a, b] : edges) {
        if (big[a] && big[b])
            throw runtime_error("Big-to-big cave edges require explicit infinite-path analysis");
        adjacency[a].push_back(b);
        adjacency[b].push_back(a);
    }
    vector<vector<u64>> w(n + 2, vector<u64>(n + 2));
    for (size_t a = 0; a < names.size(); ++a)
        if (!big[a])
            for (int b : adjacency[a]) {
                if (!big[b])
                    ++w[small[a]][small[b]];
                else
                    for (int c : adjacency[b])
                        ++w[small[a]][small[c]];
            }
    u128 part1 = w[n][n + 1], part2 = part1;
    if (!n) {
        output(part1, part2);
        return;
    }
    uint32_t limit = uint32_t(1) << n;
    vector<uint32_t> rank(limit);
    vector<uint32_t> masks, next_masks;
    for (int j = 0; j < n; ++j)
        masks.push_back(uint32_t(1) << j);
    vector<Counts> current(n);
    for (int j = 0; j < n; ++j)
        current[j].once = w[n][j];
    vector<uint32_t> neighbor(n);
    for (int u = 0; u < n; ++u)
        for (int v = 0; v < n; ++v)
            if (w[u][v])
                neighbor[u] |= uint32_t(1) << v;
    for (int k = 1; k <= n; ++k) {
        next_masks.clear();
        if (k < n) {
            uint32_t mask = (uint32_t(1) << (k + 1)) - 1;
            while (mask < limit) {
                rank[mask] = next_masks.size();
                next_masks.push_back(mask);
                uint32_t low = mask & -mask, t = mask + low;
                mask = t + (((t ^ mask) / low) >> 2);
            }
        }
        vector<Counts> next(size_t(next_masks.size()) * (k + 1));
        for (size_t mi = 0; mi < masks.size(); ++mi) {
            uint32_t mask = masks[mi];
            Counts *row = &current[mi * k];
            // Consume the optional revisit before all extensions to the next layer.
            int pos = 0;
            for (uint32_t bits = mask; bits; bits &= bits - 1, ++pos) {
                int u = countr_zero(bits);
                u128 value = row[pos].once;
                if (!value)
                    continue;
                for (uint32_t dest = neighbor[u] & mask; dest; dest &= dest - 1) {
                    int v = countr_zero(dest);
                    int vp = popcount(mask & ((uint32_t(1) << v) - 1));
                    row[vp].twice += value * w[u][v];
                }
            }
            pos = 0;
            for (uint32_t bits = mask; bits; bits &= bits - 1, ++pos) {
                int u = countr_zero(bits);
                auto value = row[pos];
                if (!value.once && !value.twice)
                    continue;
                part1 += value.once * w[u][n + 1];
                part2 += (value.once + value.twice) * w[u][n + 1];
                for (uint32_t dest = neighbor[u] & ~mask; dest; dest &= dest - 1) {
                    int v = countr_zero(dest);
                    uint32_t bit = uint32_t(1) << v;
                    size_t index = size_t(rank[mask | bit]) * (k + 1) + popcount(mask & (bit - 1));
                    next[index].once += value.once * w[u][v];
                    next[index].twice += value.twice * w[u][v];
                }
            }
        }
        cerr << "Cave layer " << k << '/' << n << " complete\n";
        masks.swap(next_masks);
        current.swap(next);
    }
    output(part1, part2);
}

u64 shortest(const Grid &input, int tiles) {
    size_t h = input.h * tiles, w = input.w * tiles, stride = w + 2, total = (h + 2) * stride;
    if (total >= numeric_limits<uint32_t>::max())
        throw runtime_error("Expanded grid exceeds 32-bit node indexing");
    // A byte of risk and a byte of queue state per cell: about 4.66 GiB for 50,000^2.
    vector<uint8_t> risk(total), state(total, 255);
    for (int ty = 0; ty < tiles; ++ty)
        for (size_t y = 0; y < input.h; ++y)
            for (int tx = 0; tx < tiles; ++tx)
                for (size_t x = 0; x < input.w; ++x)
                    risk[(ty * input.h + y + 1) * stride + tx * input.w + x + 1] =
                        (input.a[y * input.w + x] + ty + tx - 1) % 9 + 1;
    array<vector<uint32_t>, 16> buckets;
    uint32_t start = stride + 1, target = h * stride + w;
    state[start] = 0;
    buckets[0].push_back(start);
    u64 settled = 0;
    for (u64 distance = 0;; ++distance) {
        unsigned slot = distance & 15;
        auto &bucket = buckets[slot];
        for (size_t pos = 0; pos < bucket.size(); ++pos) {
            uint32_t u = bucket[pos];
            if (state[u] != slot)
                continue;
            if (u == target)
                return distance;
            state[u] = 254;
            auto relax = [&](uint32_t v) {
                unsigned weight = risk[v];
                if (!weight)
                    return;
                unsigned old = state[v];
                if (old == 254)
                    return;
                if (old == 255 || ((old - slot) & 15) > weight) {
                    unsigned next = (slot + weight) & 15;
                    state[v] = next;
                    buckets[next].push_back(v);
                }
            };
            relax(u - 1);
            relax(u + 1);
            relax(u - uint32_t(stride));
            relax(u + uint32_t(stride));
            if (++settled % 250000000 == 0)
                cerr << "Pathfinding settled " << settled << " / " << h * w << " cells\n";
        }
        bucket.clear();
    }
}
void pathfinding(istream &in, int only_tiles) {
    auto g = grid(in);
    for (auto c : g.a)
        if (!c)
            throw runtime_error("Pathfinding risks must be 1..9");
    if (only_tiles) {
        cout << shortest(g, only_tiles) << '\n';
        return;
    }
    u64 p1 = shortest(g, 1);
    cerr << "Pathfinding part 1 complete: " << p1 << '\n';
    output(p1, shortest(g, 5));
}

i64 floor_div(i64 a, i64 b) {
    i64 q = a / b, r = a % b;
    return q - (r < 0);
}
i64 ceil_div(i64 a, i64 b) {
    return -floor_div(-a, b);
}
struct Event {
    i64 x, y0, y1;
    int delta;
    bool operator<(const Event &b) const {
        return x < b.x;
    }
};
class UnionLength {
    const vector<i64> &y;
    vector<int> cover;
    vector<u64> length;
    void update(size_t p, int lo, int hi, int ql, int qh, int delta) {
        if (ql >= hi || qh <= lo)
            return;
        if (ql <= lo && hi <= qh)
            cover[p] += delta;
        else {
            int mid = (lo + hi) / 2;
            update(p * 2, lo, mid, ql, qh, delta);
            update(p * 2 + 1, mid, hi, ql, qh, delta);
        }
        length[p] = cover[p]       ? u64(y[hi] - y[lo])
                    : hi - lo == 1 ? 0
                                   : length[p * 2] + length[p * 2 + 1];
    }

  public:
    explicit UnionLength(const vector<i64> &coords)
        : y(coords), cover(coords.size() * 4), length(coords.size() * 4) {}
    void add(i64 lo, i64 hi, int delta) {
        int l = lower_bound(y.begin(), y.end(), lo) - y.begin(),
            r = lower_bound(y.begin(), y.end(), hi) - y.begin();
        update(1, 0, int(y.size()) - 1, l, r, delta);
    }
    u64 size() const {
        return length[1];
    }
};
void projectile(istream &in) {
    string text((istreambuf_iterator<char>(in)), {});
    auto v = parse_numbers(text);
    if (v.size() != 4)
        throw runtime_error("Expected xmin xmax ymin ymax");
    i64 xmin = v[0], xmax = v[1], ymin = v[2], ymax = v[3];
    if (xmax < 0) {
        i64 a = -xmax;
        xmax = -xmin;
        xmin = a;
    }
    if (xmin <= 0 || xmin > xmax || ymin > ymax || ymax >= 0)
        throw runtime_error("Projectile solver requires target wholly left/right and below origin");
    if (xmax > 1000000000 || ymin < -10000000)
        throw runtime_error("Projectile bounds exceed supported exact-sweep range");
    i64 stall_lo = 0, stall_hi = 0;
    while (stall_lo * (stall_lo + 1) / 2 < xmin)
        ++stall_lo;
    while ((stall_hi + 1) * (stall_hi + 2) / 2 <= xmax)
        ++stall_hi;
    vector<Event> events;
    vector<i64> ys;
    i64 best = numeric_limits<i64>::min();
    auto rectangle = [&](i64 x0, i64 x1, i64 y0, i64 y1) {
        if (x0 > x1 || y0 > y1)
            return;
        events.push_back({x0, y0, y1 + 1, 1});
        events.push_back({x1 + 1, y0, y1 + 1, -1});
        ys.push_back(y0);
        ys.push_back(y1 + 1);
        best = max(best, y1);
    };
    // For a target below zero, every hit occurs by -2*ymin steps.
    for (i64 t = 1; t <= -2 * ymin; ++t) {
        i64 tri = t * (t - 1) / 2, lo = ceil_div(ymin + tri, t), hi = floor_div(ymax + tri, t);
        if (lo > hi)
            continue;
        rectangle(max(t, ceil_div(xmin + tri, t)), floor_div(xmax + tri, t), lo, hi);
        rectangle(stall_lo, min(stall_hi, t - 1), lo, hi);
    }
    if (events.empty()) {
        output(0, 0);
        return;
    }
    sort(events.begin(), events.end());
    sort(ys.begin(), ys.end());
    ys.erase(unique(ys.begin(), ys.end()), ys.end());
    UnionLength tree(ys);
    u128 count = 0;
    i64 previous = events[0].x;
    for (size_t i = 0; i < events.size();) {
        i64 x = events[i].x;
        count += u128(x - previous) * tree.size();
        while (i < events.size() && events[i].x == x) {
            auto e = events[i++];
            tree.add(e.y0, e.y1, e.delta);
        }
        previous = x;
    }
    output(best > 0 ? u128(best) * (best + 1) / 2 : 0, count);
}
int main(int argc, char **argv) {
    try {
        if (argc < 3)
            throw runtime_error("Usage: solver DAY INPUT [TILES for day 15]");
        int day = stoi(argv[1]);
        ifstream in(argv[2]);
        if (!in)
            throw runtime_error("Cannot open input");
        switch (day) {
        case 4:
            bingo(in);
            break;
        case 5:
            vents(in);
            break;
        case 9:
            basins(in);
            break;
        case 11:
            octopi(in);
            break;
        case 12:
            caves(in);
            break;
        case 15:
            pathfinding(in, argc > 3 ? stoi(argv[3]) : 0);
            break;
        case 17:
            projectile(in);
            break;
        default:
            throw runtime_error("Unsupported native day");
        }
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}
