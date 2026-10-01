import re, csv, time
BIG = r"C:\Users\maith\Downloads\Cafeteria Order Data\Cafeteria Order Data.sql"
tok = re.compile(rb"'(?:[^'\\]|\\.|'')*'|[^,'\s][^,']*")

def parse(line, n):
    out = []
    for m in tok.finditer(line, 1):
        out.append(m.group(0).strip())
        if len(out) >= n:
            break
    res = []
    for t in out:
        if t == b"NULL":
            res.append("")
        elif t[:1] == b"'":
            res.append(t[1:-1].decode("utf8", "ignore"))
        else:
            res.append(t.decode("utf8", "ignore"))
    return res

O_COLS = {0:"id",1:"order_number",3:"order_status",6:"order_date",8:"branch_id",
          10:"counter_id",12:"order_through",13:"sub_total",14:"tax_amount",
          18:"discount_amount",19:"mode_of_transaction",28:"grand_total",30:"paid_or_cancel"}
D_COLS = {0:"id",1:"order_id",2:"dish_id",9:"dish_name",10:"order_quantity",
          15:"dish_price",17:"dish_cal_price",18:"counter_id"}

fo = open("data/orders_clean.csv", "w", newline="", encoding="utf8")
fd = open("data/order_details_clean.csv", "w", newline="", encoding="utf8")
wo, wd = csv.writer(fo), csv.writer(fd)
wo.writerow(O_COLS.values()); wd.writerow(D_COLS.values())

cur = None; read = 0; nxt = 1 << 30; no = nd = bad = 0; t0 = time.time()
with open(BIG, "rb") as f:
    for line in f:
        read += len(line)
        if line.startswith(b"INSERT INTO `"):
            cur = line.split(b"`")[1]
        elif line.startswith(b"(") and cur in (b"orders", b"order_details"):
            if cur == b"orders":
                v = parse(line, 31)
                if len(v) < 31: bad += 1; continue
                wo.writerow([v[i] for i in O_COLS]); no += 1
            else:
                v = parse(line, 19)
                if len(v) < 19: bad += 1; continue
                wd.writerow([v[i] for i in D_COLS]); nd += 1
        elif line.startswith(b"CREATE TABLE"):
            cur = None
        if read >= nxt:
            print(f"{read/1e9:.1f} GB, orders={no:,}, details={nd:,}, {time.time()-t0:.0f}s", flush=True)
            nxt += 1 << 30
fo.close(); fd.close()
print("DONE orders", no, "details", nd, "bad rows", bad)
