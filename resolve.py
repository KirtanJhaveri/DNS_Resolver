"""
resolve.py: a recursive resolver built using dnspython
"""

import argparse

import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

FORMATS = (
    ("CNAME", "{alias} is an alias for {name}"),
    ("A", "{name} has address {address}"),
    ("AAAA", "{name} has IPv6 address {address}"),
    ("MX", "{name} mail is handled by {preference} {exchange}"),
)

ROOT_SERVERS = (
    "192.228.79.201",
    "192.33.4.12",
    "199.7.91.13",
    "192.203.230.10",
    "192.5.5.241",
    "192.112.36.4",
    "198.97.190.53",
    "192.36.148.17",
    "192.58.128.30",
    "193.0.14.129",
    "199.7.83.42",
    "202.12.27.33",
    "198.41.0.4",
)

cache = {}
intermediate_cache = {}


def collect_results(name: str) -> dict:
    # pylint: disable = E, W, R, C

    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """
    full_response = {}
    cnames = []
    arecords = []
    aaaarecords = []
    mxrecords = []

    target_name = dns.name.from_text(name)

    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME)

    if response is not None:
        for answers in response.answer:
            for answer in answers:
                cnames.append({"name": answer, "alias": name})

                # Use CNAME answer for the remaining lookups
                target_name = str(answer)[:-1]

    # lookup A
    response = lookup(target_name, dns.rdatatype.A)

    if response is not None:
        for answers in response.answer:
            a_name = answers.name
            for answer in answers:
                if answer.rdtype == 1:  # A record
                    arecords.append({"name": a_name, "address": str(answer)})

    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA)

    if response is not None:
        for answers in response.answer:
            aaaa_name = answers.name
            for answer in answers:
                if answer.rdtype == 28:  # AAAA record
                    aaaarecords.append({"name": aaaa_name,
                                        "address": str(answer)})

    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX)

    if response is not None:
        for answers in response.answer:
            mx_name = answers.name
            for answer in answers:
                if answer.rdtype == 15:  # MX record
                    mxrecords.append(
                        {
                            "name": mx_name,
                            "preference": answer.preference,
                            "exchange": str(answer.exchange),
                        }
                    )

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords

    return full_response


# Get IPv4 address
def get_addr(string):
    """
    Get IP address
    """
    token = string.split()
    address = []
    for i_token in token:
        if i_token == "A":
            address += [token[-1]]

    return address


def r_lookup(target_name, qtype, s_lst, flag=False):
    # pylint: disable = E, W, R, C

    """
    DNS resolver function.
    """
    if not s_lst:
        return None

    url_split = str(target_name).split(".")
    get_domain = url_split[len(url_split) - 2]
    if get_domain not in intermediate_cache:
        intermediate_cache[get_domain] = {}

    create_msg = dns.message.make_query(target_name, qtype)
    resp = None
    for server in s_lst:
        try:
            if server in intermediate_cache[get_domain] and flag:

                resp = intermediate_cache[get_domain][server]
            elif flag:

                resp = dns.query.udp(create_msg, server, 3)
                intermediate_cache[get_domain][server] = resp
            else:
                resp = dns.query.udp(create_msg, server, 3)
        except dns.exception.DNSException:

            continue

        if not resp.answer:
            ip_addr = []

            if not resp.additional:
                ns_names = []

                for auth_list in resp.authority:

                    for auth in auth_list:
                        if auth.rdtype == 6:
                            return None
                        ns_names += [str(auth)[:-1]]

                    for n in ns_names:

                        ns_resp = r_lookup(n, 1, ROOT_SERVERS)

                        if ns_resp is not None:
                            for answer in ns_resp.answer:
                                ns_address = get_addr(str(answer))

                                ns_response2 = r_lookup(target_name, qtype,
                                                        ns_address)
                                if ns_response2 is not None:
                                    return ns_response2

            else:
                for additional in resp.additional:
                    ip_addr += get_addr(str(additional))

                return r_lookup(target_name, qtype, ip_addr)

        else:
            for ans in resp.answer:
                for answer in ans:
                    target_name = str(answer)[:-1]

                    if answer.rdtype == qtype:
                        return resp
                    else:
                        if answer.rdtype == 5:
                            return r_lookup(target_name, qtype, ROOT_SERVERS)
    return None


def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata) -> dns.message.Message:
    """
    This function uses a recursive resolver to find the relevant answer to the
    query.
    """
    return r_lookup(target_name, qtype, ROOT_SERVERS, True)


def print_results(results: dict) -> None:
    """
    Take the results of a `lookup` and print them to the screen like the host
    program would.
    """

    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument(
        "-v", "--verbose", help="increase output verbosity",
        action="store_true"
    )
    program_args = argument_parser.parse_args()
    for a_domain_name in program_args.name:
        if a_domain_name in cache:
            print_results(cache[a_domain_name])
        else:
            cache[a_domain_name] = collect_results(a_domain_name)
            print_results(cache[a_domain_name])


if __name__ == "__main__":
    main()
