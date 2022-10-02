from .site import Site

def build(args, conf):
    print("Building site...")
    print(f"Target is: {args.target}")
    site = Site(args, conf)
    site.build()
