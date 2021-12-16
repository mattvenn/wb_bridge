# test wb_bridge_2way

import cocotb
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotbext.wishbone.driver import WishboneMaster, WBOp
from cocotbext.wishbone.monitor import WishboneSlave


async def reset(dut):
    dut.wb_rst_i = 1
    dut.wb_rst_i = 0
    await ClockCycles(dut.wb_clk_i, 10)
    dut.wb_rst_i = 0
    await ClockCycles(dut.wb_clk_i, 10)


async def test_wbm_set(wbm_bus, addr, value):
    """
    Test putting values into the given wishbone address.
    """
    await wbm_bus.send_cycle([WBOp(addr, value)])

async def test_wbm_get(wbm_bus, addr):
    """
    Test getting values from the given wishbone address.
    """
    res_list = await wbm_bus.send_cycle([WBOp(addr)])
    rvalues = [entry.datrd for entry in res_list]
    return rvalues[0]


@cocotb.test()
async def test_wb_bridge_2way(dut):

    clock = Clock(dut.wb_clk_i, 10, units="us")

    cocotb.fork(clock.start())

    wbm_signals_dict = {
        "cyc"   :   "wbs_cyc_i",
        "stb"   :   "wbs_stb_i",
        "we"    :   "wbs_we_i",
        "adr"   :   "wbs_adr_i",
        "datwr" :   "wbs_dat_i",
        "datrd" :   "wbs_dat_o",
        "ack"   :   "wbs_ack_o"
    }

    wbsa_signals_dict = {
        "cyc"   :   "wbm_a_cyc_o",
        "stb"   :   "wbm_a_stb_o",
        "we"    :   "wbm_a_we_o",
        "adr"   :   "wbm_a_adr_o",
        "datwr" :   "wbm_a_dat_i",
        "datrd" :   "wbm_a_dat_o",
        "ack"   :   "wbm_a_ack_i"
    }

    wbsa_signals_dict = {
        "cyc"   :   "wbm_b_cyc_o",
        "stb"   :   "wbm_b_stb_o",
        "we"    :   "wbm_b_we_o",
        "adr"   :   "wbm_b_adr_o",
        "datwr" :   "wbm_b_dat_i",
        "datrd" :   "wbm_b_dat_o",
        "ack"   :   "wbm_b_ack_i"
    }

    wbm_bus = WishboneMaster(dut, "", dut.wb_clk_i, width=32, timeout=10, signals_dict=wbm_signals_dict)
    wbsa_bus = WishboneSlave(dut, "", dut.wb_clk_i, signals_dict=wbsa_signals_dict)
    wbsb_bus = WishboneSlave(dut, "", dut.wb_clk_i, signals_dict=wbsa_signals_dict)

    await reset(dut)

    busa_base_adr = 0x3000_0000
    busb_base_adr = 0x30ff_fc00

    wbsa_bus._recvQ.clear()
    wbsb_bus._recvQ.clear()

    await test_wbm_set(wbm_bus, busa_base_adr, 0xdeadbeef)
#    assert wbsa_bus._recvQ.count == 1
#    wbsa_bus._recvQ.clear()


