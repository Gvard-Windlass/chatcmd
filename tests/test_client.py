import sys
import pexpect


def prepare_python_script(target_script: str) -> pexpect.spawn:
    child = pexpect.spawn("bash")

    child.expect(r"\$")
    child.sendline("cd /mnt/c/Dev/chatcmd")
    child.expect(r"\$")
    if target_script == "server":
        child.sendline(f"python -m chatcmd.{target_script} run_local")
    else:
        child.sendline(f"python -m chatcmd.{target_script}")

    return child


def test_connection():
    server = prepare_python_script("server")
    server.timeout = None
    server.expect("Running local database")

    client1 = prepare_python_script("client")
    client2 = prepare_python_script("client")
    client1.logfile = sys.stdout.buffer

    try:
        client1.expect("Enter username and password: ")
        client2.expect("Enter username and password: ")

        client1.sendline("gvard abc123!@#")
        client2.sendline("alice 123abc!@#")

        client1.expect("gvard connected!")
        client2.expect("alice connected!")

        client1.sendline("hello")
        client1.expect("gvard: hello")

        client2.sendline("how it's going?")
        client2.expect("alice: how it's going?")
        client1.expect("alice: how it's going?")

        client1.sendline("\\q")
        client2.expect("gvard has left the chat")

        server.close()
        client2.expect("Server closed connection")
    finally:
        server.close()
        client1.close()
        client2.close()
