# VampSecure Labs

Suite of educational cybersecurity tools built under [VampSecure Studios](https://vampsecurestudios.com). Each tool demonstrates a specific security concept with clean, documented Python or C code.

**For educational and authorized security research use only.**

---

## Tools

| Tool | Language | Description |
|---|---|---|
| [arp_sentinel](scripts/arp_sentinel/) | Python · Scapy | ARP spoofing detector + attacker PoC |
| [cve_oracle](scripts/cve_oracle/) | Python | CVE analyzer with NIST NVD + OTX threat intel |
| [entropy_watch](scripts/entropy_watch/) | Python | Shannon entropy ransomware detector |
| [icmp-tunnel](scripts/icmp-tunnel/) | Python · Scapy | Covert ICMP channel (XOR + Base64) |
| [passive_recon](scripts/passive_recon/) | Python · asyncio | Passive subdomain enumeration + HTTP header analysis |
| [shellcode_runner](scripts/shellcode_runner/) | C · ARM64 asm | mmap RWX + syscall shellcode lab |

---

## Quick Start (Docker)

```bash
git clone https://github.com/belky-me/vampsecure-labs
cd vampsecure-labs
cp scripts/passive_recon/.env.example scripts/passive_recon/.env
# Edit .env and add your OTX_API_KEY (optional)
docker compose up -d
```

## Requirements

```bash
pip install -r requirements.txt
```

Some tools require **root / sudo** (Scapy raw sockets for ARP and ICMP).

---

## Legal

All tools are for use in controlled lab environments, CTF competitions, or authorized security assessments only. Unauthorized use against systems you do not own or have explicit permission to test may be illegal.

---

Made with ☠️ by [VampSecure Studios](https://vampsecurestudios.com) · [@belky-me](https://github.com/belky-me)
