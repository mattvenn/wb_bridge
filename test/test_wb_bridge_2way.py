# test wb_bridge_2way

import cocotb
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotbext.wishbone.driver import WishboneMaster, WBOp
from cocotbext.wishbone.monitor import WishboneSlave
from wb_ram import WishboneRAM

async def reset(dut):
    dut.wb_rst_i = 1
    dut.wb_rst_i = 0
    await ClockCycles(dut.wb_clk_i, 10)
    dut.wb_rst_i = 0
    await ClockCycles(dut.wb_clk_i, 10)


async def wbm_write(wbm_bus, addr, value):
    await wbm_bus.send_cycle([WBOp(addr, value)])

async def wbm_read(wbm_bus, addr):
    res_list = await wbm_bus.send_cycle([WBOp(addr)])
    rvalues = [entry.datrd for entry in res_list]
    return rvalues[0]


def init_ram(ram_bus, size, prefix): 
    for addr in range(size-1):
        ram_bus.data[addr] = addr | prefix


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
        "ack"   :   "wbs_ack_o",
        "sel"   :   "wbs_sel_i",
    }

    wbsa_signals_dict = {
        "cyc"   :   "wbm_a_cyc_o",
        "stb"   :   "wbm_a_stb_o",
        "we"    :   "wbm_a_we_o",
        "adr"   :   "wbm_a_adr_o",
        "datrd" :   "wbm_a_dat_i",
        "datwr" :   "wbm_a_dat_o",
        "ack"   :   "wbm_a_ack_i",
        "sel"   :   "wbm_a_sel_o"
    }

    wbsb_signals_dict = {
        "cyc"   :   "wbm_b_cyc_o",
        "stb"   :   "wbm_b_stb_o",
        "we"    :   "wbm_b_we_o",
        "adr"   :   "wbm_b_adr_o",
        "datrd" :   "wbm_b_dat_i",
        "datwr" :   "wbm_b_dat_o",
        "ack"   :   "wbm_b_ack_i",
        "sel"   :   "wbm_b_sel_o"
    }

    wbm_bus = WishboneMaster(dut, "", dut.wb_clk_i, width=32, timeout=10, signals_dict=wbm_signals_dict)
#    wbsa_bus = WishboneSlave(dut, "", dut.wb_clk_i, signals_dict=wbsa_signals_dict)
#    wbsb_bus = WishboneSlave(dut, "", dut.wb_clk_i, signals_dict=wbsa_signals_dict)

    busa_base_adr = 0x3000_0000
    busb_base_adr = 0x30ff_fc00
    busb_end_adr = 0x30ff_ffff

    wbsa_size = busb_base_adr - busa_base_adr
    wbsa_bus = WishboneRAM(dut, dut.wb_clk_i, wbsa_signals_dict, wbsa_size, busa_base_adr)
    print(wbsa_size)
    init_ram(wbsa_bus, wbsa_size, busa_base_adr)

    wbsb_size = busb_end_adr - busb_base_adr + 1
    print(wbsb_size)
    wbsb_bus = WishboneRAM(dut, dut.wb_clk_i, wbsb_signals_dict, wbsb_size, busb_base_adr)
    init_ram(wbsb_bus, wbsb_size, busb_base_adr)

    await reset(dut)

    dut.wbs_sel_i = 0xf

#    wbsa_bus._recvQ.clear()
#    wbsb_bus._recvQ.clear()

    await wbm_write(wbm_bus, busa_base_adr, 0xdeadbeef)
#    assert wbsa_bus._recvQ.count == 1
#    wbsa_bus._recvQ.clear()


