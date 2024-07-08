from lib import parse_ad_html

def main():
    with open("../../data/parttime.html") as f:
        parttime =  ("parttime", f.read())
    with open("../../data/fulltime.html") as f:
        fulltime = ("fulltime", f.read())
    with open("../../data/management.html") as f:
        management = ("management", f.read())

    for t in [parttime, fulltime, management]:
        r = parse_ad_html(t[1], t[0])
        if t[1] != "parttime":
            c = r["content"][0:20]
            del r["content"]
            print(r, c)
        else:
            print(r)

if __name__ == "__main__":
    main()
