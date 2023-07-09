import pexpect


def test_connection():
    client = pexpect.spawn("bash")
    server = pexpect.spawn("bash", timeout=None)
    try:
        server.expect(r"\$")
        server.sendline("cd /mnt/c/Dev/chatcmd")
        server.expect(r"\$")
        server.sendline("python -m chatcmd.server")

        # uncomment to see output
        # client.logfile = sys.stdout.buffer

        client.expect(r"\$")
        client.sendline("cd /mnt/c/Dev/chatcmd")
        client.expect(r"\$")
        client.sendline("python -m chatcmd.client")
        client.expect("Enter username: ")

        client.sendline("gvard")
        client.expect("gvard connected!")
        client.sendline("hello")
        client.expect("gvard: hello")

        server.close()
        client.expect("Server closed connection")

        client.close()
    finally:
        client.close()
        server.close()
