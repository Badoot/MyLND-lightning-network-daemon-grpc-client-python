# Grab the data

import gRPCfiles.rpc_pb2 as ln
import gRPCfiles.rpc_pb2_grpc as lnrpc
import gRPCfiles.client_pb2 as loop
import gRPCfiles.client_pb2_grpc as looprpc
import grpc
import os
import arg_parser as arg_parser
import codecs


args = arg_parser.arg_parser_func()

# # # # # # # # # # # # # 
#   Set node variables
# # # # # # # # # # # # # 

# Default ip:port is localhost:10009
if args.ip_port:
    ip_port = args.ip_port
else:
    ip_port = 'localhost:10009'

# Default data_dir is '/root/.lnd'
if args.lnddir:
    lnddir = args.lnddir
else:
    lnddir = '/root/.lnd'

# Default tlspath is '/root/.lnd'
if args.tlspath:
    tlspath = args.tlspath
else:
    tlspath = '/root/.lnd'

# Default macaroonpath is '/root/.lnd'
if args.macaroonpath:
    macaroonpath = args.macaroonpath
else:
    macaroonpath = '/root/.lnd'

class APICall():
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(tlspath + '/tls.cert', 'rb').read()

    def metadata_callback(self, callback):
        macaroon = codecs.encode(open(macaroonpath + '/admin.macaroon', 'rb').read(), 'hex')
        callback([('macaroon', macaroon)], None)

    ssl_creds = grpc.ssl_channel_credentials(cert)
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    combined_cred = grpc.composite_channel_credentials(ssl_creds, auth_creds)
    channel = grpc.secure_channel(ip_port, combined_cred)
    stub = lnrpc.LightningStub(channel)
    wallet_stub = lnrpc.WalletUnlockerStub(channel)


# # # # # # # # # #
#   My LND node
# # # # # # # # # #

def get_info():
    response = APICall.stub.GetInfo(ln.GetInfoRequest())
    return response


def get_set_debug_level(show, level_spec):
    request = ln.DebugLevelRequest(
        show=show,
        level_spec=level_spec
    )
    response = APICall.stub.DebugLevel(request)
    return response


def get_fee_report():
    response = APICall.stub.FeeReport(ln.FeeReportRequest())
    return response


# # # # # # # # # # # # # # #
#   Lightning Network
# # # # # # # # # # # # # # #


def get_network_info():
    response = APICall.stub.GetNetworkInfo(ln.NetworkInfoRequest())
    return response


def get_describe_graph():
    response = APICall.stub.DescribeGraph(ln.ChannelGraphRequest())
    return response


# # # # # # # # # #
#      Peers
# # # # # # # # # #

def get_peers():
    response = APICall.stub.ListPeers(ln.ListPeersRequest())
    return response


def get_node_info(pub_key):
    response = APICall.stub.GetNodeInfo(ln.NodeInfoRequest(pub_key=pub_key))
    return response


def get_connect_peer(peer_data):
    data = peer_data.split('@')
    pubkey = str(data[0])
    host = str(data[1])
    ln_address = ln.LightningAddress(pubkey=pubkey, host=host)
    request = ln.ConnectPeerRequest(addr=ln_address, perm=False)
    response = APICall.stub.ConnectPeer(request)
    return response


def get_disconnect_peer(pub_key):
    request = ln.DisconnectPeerRequest(pub_key=pub_key)
    response = APICall.stub.DisconnectPeer(request)
    return response


# # # # # # # # # #
#    Channels
# # # # # # # # # #

def get_channels():
    response = APICall.stub.ListChannels(ln.ListChannelsRequest())
    return response


def get_pending_channels():
    response = APICall.stub.PendingChannels(ln.PendingChannelsRequest())
    return response


def get_channel_balance():
    response = APICall.stub.ChannelBalance(ln.ChannelBalanceRequest())
    return response


def get_closed_channels():
    response = APICall.stub.ClosedChannels(ln.ClosedChannelsRequest())
    return response


def get_channel_info(chan_id):
    response = APICall.stub.GetChanInfo(ln.ChanInfoRequest(chan_id=chan_id))
    return response


def get_open_channel_wait(node_pubkey=None, local_funding_amount=0, push_sat=0):
    pubkey_bytes = codecs.decode(node_pubkey, 'hex')
    request = ln.OpenChannelRequest(
        node_pubkey=pubkey_bytes,
        node_pubkey_string=node_pubkey,
        local_funding_amount=int(local_funding_amount),
        push_sat=int(push_sat)
    )
    response = APICall.stub.OpenChannel(request)
    return response


def get_close_channel(funding_tx, output_index, force):
    channel_point = ln.ChannelPoint(
        funding_txid_str=str(funding_tx),
        output_index=int(output_index),
    )
    request = ln.CloseChannelRequest(
        channel_point=channel_point,
        force=force,
        target_conf=None,
        sat_per_byte=None)
    response = APICall.stub.CloseChannel(request)
    return response


def get_open_channel(node_pubkey, local_funding_amount=None, push_sat=None):
    # pubkey_bytes = codecs.decode(node_pubkey, 'hex')
    request = ln.OpenChannelRequest(
        # node_pubkey=pubkey_bytes,
        node_pubkey_string=node_pubkey,
        local_funding_amount=int(local_funding_amount),
        push_sat=int(push_sat)
    )
    response = APICall.stub.OpenChannelSync(request)
    return response


def get_update_channel_policy(funding_tx, output_index, base_fee_msat, fee_rate, time_lock_delta):
    channel_point = ln.ChannelPoint(
        funding_txid_str=str(funding_tx),
        output_index=int(output_index),
    )
    request = ln.PolicyUpdateRequest(
        chan_point=channel_point,
        base_fee_msat=base_fee_msat,
        fee_rate=fee_rate,
        time_lock_delta=time_lock_delta
    )
    response = APICall.stub.UpdateChannelPolicy(request)
    return response


# # # # # # # # # # # # # # #
#    On-chain Transactions
# # # # # # # # # # # # # # #


def get_wallet_balance():
    response = APICall.stub.WalletBalance(ln.WalletBalanceRequest())
    return response


def get_transactions():
    response = APICall.stub.GetTransactions(ln.GetTransactionsRequest())
    return response


def get_new_address():
    response = APICall.stub.NewAddress(ln.NewAddressRequest())
    return response


def get_send_coins(addr, amount):
    request = ln.SendCoinsRequest(
        addr=str(addr),
        amount=int(amount),
    )
    response = APICall.stub.SendCoins(request)
    return response


# # # # # # # # # # # # # # #
#    Lightning Payments
# # # # # # # # # # # # # # #


def get_list_payments():
    response = APICall.stub.ListPayments(ln.ListPaymentsRequest())
    return response


def get_delete_payments():
    response = APICall.stub.DeleteAllPayments(ln.DeleteAllPaymentsRequest())
    return response


def get_list_invoices():
    response = APICall.stub.ListInvoices(ln.ListInvoiceRequest(num_max_invoices=-1))
    return response


def get_add_invoice(amount, memo):
    request = ln.Invoice(
        memo=memo,
        value=amount,
    )
    response = APICall.stub.AddInvoice(request)
    return response


def get_lookup_invoice(r_hash):
    request = ln.PaymentHash(r_hash_str=r_hash)
    response = APICall.stub.LookupInvoice(request)
    return response


def get_send_payment(payment_request, dest, payment_hash_str, amt, final_cltv_delta):
    request = ln.SendRequest(
        payment_request=payment_request,
        dest_string=dest,
        payment_hash_string=payment_hash_str,
        amt=amt,
        final_cltv_delta=final_cltv_delta,
    )
    response = APICall.stub.SendPaymentSync(request)
    return response

def get_send_to_route(payment_hash, route):
    request = ln.SendToRouteRequest(
        payment_hash = payment_hash,
        route = route
    )
    response = APICall.stub.SendToRoute(request)
    return response


def get_decode_payreq(payment_request):
    request = ln.PayReqString(pay_req=payment_request)
    response = APICall.stub.DecodePayReq(request)
    return response


def get_query_route(pub_key, amount, num_routes):
    request = ln.QueryRoutesRequest(
        pub_key=pub_key,
        amt=amount,
        num_routes=num_routes,
    )
    response = APICall.stub.QueryRoutes(request)
    return response


# # # # # # # # # # # # # # #
#    Wallet Stub Stuff
# # # # # # # # # # # # # # #


def wallet_unlock(password):
    request = ln.UnlockWalletRequest(wallet_password=password.encode())
    response = APICall.wallet_stub.UnlockWallet(request)
    return response


def change_password(current_password, new_password):
    request = ln.ChangePasswordRequest(
            current_password=current_password.encode(),
            new_password=new_password.encode()
            )
    response = APICall.wallet_stub.ChangePassword(request)
    return response


def get_gen_seed():
    request = ln.GenSeedRequest()
    response = APICall.wallet_stub.GenSeed(request)
    return response


def get_create(wallet_password, cipher_seed_mnemonic, aezeed_passphrase):
    request = ln.InitWalletRequest(
        wallet_password=wallet_password,
        cipher_seed_mnemonic=cipher_seed_mnemonic,
        aezeed_passphrase=aezeed_passphrase,
        recovery_window=int(0)
    )
    response = APICall.wallet_stub.InitWallet(request)
    return response


# # # # # # 
#   Loop 
# # # # # # 

def get_loop(amount):
    channel = grpc.insecure_channel('localhost:11010')
    stub = looprpc.SwapClientStub(channel)
    request = loop.LoopOutRequest(
        amt=amount     
    )
    response = stub.LoopOut(request)
    return response