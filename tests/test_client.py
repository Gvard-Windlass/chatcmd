import sys
import pexpect


def prepare_python_script(target_script) -> pexpect.spawn:
    child = pexpect.spawn("bash")

    child.expect(r"\$")
    child.sendline("cd /mnt/c/Dev/chatcmd")
    child.expect(r"\$")
    child.sendline(f"python -m chatcmd.{target_script}")

    return child


def test_connection():
    server = prepare_python_script("server")
    server.timeout = None

    client1 = prepare_python_script("client")
    client1.logfile = sys.stdout.buffer
    client2 = prepare_python_script("client")

    try:
        client1.expect("Enter username: ")
        client2.expect("Enter username: ")

        client1.sendline("gvard")
        client2.sendline("alice")

        client1.expect("gvard connected!")
        client2.expect("alice connected!")

        client1.sendline("hello")
        client1.expect("gvard: hello")

        client2.sendline("how it's going?")
        client2.expect("alice: how it's going?")
        client1.expect("alice: how it's going?")

        server.close()
        client1.expect("Server closed connection")

    finally:
        server.close()
        client1.close()
        client2.close()
