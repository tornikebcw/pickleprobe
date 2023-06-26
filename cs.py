import toml


def heimdallRpc():
    try:
        heimdallconfig = './heimdall.toml'
        with open(heimdallconfig, 'r') as file:
            parsed_toml = toml.load(file)

        if 'bor_rpc_url' in parsed_toml:
            if parsed_toml['bor_rpc_url'] == "http://localhost:8545":
                print("The bor_rpc_url is set to localhost.")
            else:
                print("The bor_rpc_url is  set to External Provider.")
        else:
            print("The bor_rpc_url setting could not be found.")
    except Exception as err:
        print(f"An error occurred: {err}")


heimdallRpc()
