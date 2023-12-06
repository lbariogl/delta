import ROOT
import argparse

kBlueC = ROOT.TColor.GetColor('#1f78b4')
kOrangeC = ROOT.TColor.GetColor('#ff7f00')
ROOT.gROOT.SetBatch()
# silent mode for fits
ROOT.RooMsgService.instance().setSilentMode(True)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
ROOT.gROOT.LoadMacro(r'RooCustomPdfs/RooGausExp.cxx++')
# ROOT.gROOT.LoadMacro('RooCustomPdfs/RooVoigtianExp.cxx++')

parser = argparse.ArgumentParser(
    description='Configure the parameters of the script.')
parser.add_argument('--mc', dest='mc', action='store_true',
                    help="if True MC information is stored.", default=False)
args = parser.parse_args()

mc = args.mc

def lift_histo(histo):
    offset = histo.GetBinContent(histo.GetMinimumBin())
    if offset >= 0:
        return
    n_bins = histo.GetXaxis().GetNbins()
    for i in range(1, n_bins+1):
        content = histo.GetBinContent(i)
        histo.SetBinContent(i, content - offset)

# project histograms onto pt bins
def createHistograms(label, res_dir):

    histo_2D_SE = input_dir.Get(f'h{label}InvMass')
    histo_2D_ME = input_dir.Get(f'h{label}InvMassEM')
    if mc:
        histo_2D_Gen = input_dir.Get(f'h{label}InvMassGen')

    hMass = []
    hMass_EM = []
    hMass_diff = []
    cComp = []
    if mc:
        hMass_Gen = []

    for i_pt in range(1, histo_2D_SE.GetXaxis().GetNbins() + 1):
        print(f'pt bin {i_pt} / {histo_2D_SE.GetXaxis().GetNbins()}')
        pt_title = str(histo_2D_SE.GetXaxis().GetBinLowEdge(i_pt)) + r' #leq #it{p}_{T} < ' + str(
            histo_2D_SE.GetXaxis().GetBinLowEdge(i_pt + 1)) + r' (GeV/#it{c})'
        # same-event
        histo_SE = histo_2D_SE.ProjectionY(
            f'h{label}_SE_{i_pt}', i_pt, i_pt)
        histo_SE.SetTitle(pt_title)
        histo_SE.SetMarkerStyle(20)
        histo_SE.SetMarkerColor(ROOT.kRed+1)
        histo_SE.SetLineColor(ROOT.kRed+1)
        hMass.append(histo_SE)
        res_dir.cd('same-event')
        histo_SE.Write()
        # mixed-event
        histo_ME = histo_2D_ME.ProjectionY(
            f'h{label}_ME_{i_pt}', i_pt, i_pt)
        histo_ME.SetTitle(pt_title)
        histo_ME.SetMarkerStyle(20)
        histo_ME.SetMarkerColor(ROOT.kAzure+2)
        histo_ME.SetLineColor(ROOT.kAzure+2)
        hMass_EM.append(histo_ME)
        res_dir.cd('mixed-event')
        histo_ME.Write()
        # difference
        canvas = ROOT.TCanvas(
            f'cComp{label}_{i_pt}', f'cComp{label}_{i_pt}', 800, 600)
        epsilon = 0.001
        firt_scale_bin = histo_SE.FindBin(1.5+epsilon)
        last_scale_bin = histo_SE.FindBin(1.8-epsilon)
        scale_factor = histo_SE.Integral(
            firt_scale_bin, last_scale_bin) / histo_ME.Integral(firt_scale_bin, last_scale_bin)
        histo_ME.Scale(scale_factor)
        histo_SE.Draw('PE')
        histo_ME.Draw('PE SAME')
        legend = ROOT.TLegend(0.6, 0.7, 0.9, 0.8, '', 'brNDC')
        legend.AddEntry(histo_SE, 'Same event', 'PE')
        legend.AddEntry(histo_ME, 'Mixed events', 'PE')
        legend.Draw()
        cComp.append(canvas)
        res_dir.cd('comp')
        canvas.Write()
        histo_diff = histo_SE.Clone(f'h{label}_diff_{i_pt}')
        histo_diff.SetDirectory(0)
        histo_diff.Add(histo_ME, -1.)
        lift_histo(histo_diff)
        histo_diff.SetMarkerStyle(20)
        histo_diff.SetMarkerColor(ROOT.kBlack)
        histo_diff.SetLineColor(ROOT.kBlack)
        hMass_diff.append(histo_diff)

        # create roofit routine
        mass = ROOT.RooRealVar('m', 'm', 1.1, 1.8, 'GeV/c^{2}')

        # signal
        mu = ROOT.RooRealVar('mu', '#mu', 1.2, 1.4, 'GeV/c^{2}')
        # gamma = ROOT.RooRealVar('gamma', '#Gamma', 0.05, 0.4, 'GeV/c^{2}')
        sigma = ROOT.RooRealVar('sigma', '#Sigma', 0.01, 0.07, 'GeV/c^{2}')
        tau = ROOT.RooRealVar('tau', '#tau', 0.01, 0.8, 'GeV/c^{2}')


        # signal = ROOT.RooVoigtianExp(
        #     'voigt_exp', 'voigt_exp', mass, mu, gamma, sigma, tau, True)

        signal = ROOT.RooGausExp('gauss_exp', 'gauss_exp signal', mass, mu, sigma, tau)
        # background
        c0 = ROOT.RooRealVar('c0', 'constant c0', -1.5, 1.)

        background = ROOT.RooChebychev('bkg', 'pol1 bkg', mass, ROOT.RooArgList(c0))

        # total
        n_signal = ROOT.RooRealVar('n_signal', 'n_signal', 0., 1e6)
        n_background = ROOT.RooRealVar('n_background', 'n_background', 0., 1e6)

        model = ROOT.RooAddPdf('total_pdf', 'signal + background', ROOT.RooArgList(
            signal, background), ROOT.RooArgList(n_signal, n_background))

        rooMass_diff = ROOT.RooDataHist(f'rooMass_{i_pt}', pt_title, ROOT.RooArgList(mass), ROOT.RooFit.Import(histo_diff, False))
        model.fitTo(rooMass_diff, ROOT.RooFit.Range(1.1, 1.8), ROOT.RooFit.Verbose(False))

        # retrieve parameteres from fit
        frame = mass.frame()
        frame.SetName(f'f{label}_diff_{i_pt}')
        frame.SetTitle(pt_title)
        rooMass_diff.plotOn(frame, ROOT.RooFit.Name('data'), ROOT.RooFit.DrawOption('pz'), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
        model.plotOn(frame, ROOT.RooFit.Components('bkg'), ROOT.RooFit.LineStyle(
            ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed+1))
        model.plotOn(frame, ROOT.RooFit.LineColor(
            ROOT.kAzure+1), ROOT.RooFit.Name('total_pdf'))

        chi2 = frame.chiSquare('total_pdf', 'data')

        # add pave for stats
        pinfo_vals = ROOT.TPaveText(0.632, 0.5, 0.932, 0.85, 'NDC')
        pinfo_vals.SetBorderSize(0)
        pinfo_vals.SetFillStyle(0)
        pinfo_vals.SetTextAlign(11)
        pinfo_vals.SetTextFont(42)
        pinfo_vals.AddText(
            '#mu = ' + f'{mu.getVal():.3f} #pm {mu.getError():.3f}' + ' GeV/#it{c}^{2}')
        # pinfo_vals.AddText(
        #     '#Gamma = ' + f'{gamma.getVal():.3f} #pm {gamma.getError():.3f}' + ' GeV/#it{c}^{2}')
        pinfo_vals.AddText(
            '#sigma = ' + f'{sigma.getVal():.3f} #pm {sigma.getError():.3f}' + ' GeV/#it{c}^{2}')
        pinfo_vals.AddText(
            '#tau = ' + f'{tau.getVal():.3f} #pm {tau.getError():.3f}' + ' GeV/#it{c}^{2}')
        pinfo_vals.AddText(
            'N_{signal} = ' + f'{n_signal.getVal():.0f} #pm {n_signal.getError():.0f}')
        pinfo_vals.AddText(
            'c_{0} = ' + f'{c0.getVal():.3f} #pm {c0.getError():.3f}')
        pinfo_vals.AddText(
            'N_{background} = ' + f'{n_background.getVal():.0f} #pm {n_background.getError():.0f}')
        pinfo_vals.AddText(
            '#chi^{2} = ' + f'{chi2:.2f}')
        frame.addObject(pinfo_vals)
        res_dir.cd('diff')
        frame.Write()

        if mc:
            histo_gen = histo_2D_Gen.ProjectionY(
                f'h{label}_Gen_{i_pt}', i_pt, i_pt)
            histo_gen.SetTitle(pt_title)
            histo_gen.SetMarkerStyle(20)
            histo_gen.SetMarkerColor(ROOT.kGreen+3)
            histo_gen.SetLineColor(ROOT.kGreen+3)
            hMass_Gen.append(histo_gen)
            res_dir.cd('generated')
            histo_gen.Write()

    if mc:
        return hMass, hMass_EM, hMass_diff, hMass_Gen, cComp
    else:
        return hMass, hMass_EM, hMass_diff, cComp


# input
input_file = ROOT.TFile.Open('mc/AnalysisResults_train.root')
input_dir = input_file.Get('deltaAnalysis')

# output
output_file = ROOT.TFile('delta.root', 'recreate')

# Delta++
deltaplusplus_dir = output_file.mkdir('delta_plusplus')
deltaplusplus_dir.mkdir('same-event')
deltaplusplus_dir.mkdir('mixed-event')
deltaplusplus_dir.mkdir('comp')
deltaplusplus_dir.mkdir('diff')
if mc:
    deltaplusplus_dir.mkdir('generated')

print('Delta++')
createHistograms(label='DeltaPlusPlus', res_dir=deltaplusplus_dir)

# AntiDelta++
antideltaplusplus_dir = output_file.mkdir('antidelta_plusplus')
antideltaplusplus_dir.mkdir('same-event')
antideltaplusplus_dir.mkdir('mixed-event')
antideltaplusplus_dir.mkdir('comp')
antideltaplusplus_dir.mkdir('diff')
if mc:
    antideltaplusplus_dir.mkdir('generated')

print('AntiDelta++')
createHistograms(label='AntiDeltaPlusPlus', res_dir=antideltaplusplus_dir)

# Delta0
deltazero_dir = output_file.mkdir('delta_zero')
deltazero_dir.mkdir('same-event')
deltazero_dir.mkdir('mixed-event')
deltazero_dir.mkdir('comp')
deltazero_dir.mkdir('diff')
if mc:
    deltazero_dir.mkdir('generated')

print('Delta0')
createHistograms(label='DeltaZero', res_dir=deltazero_dir)

# AntiDelta0
antideltazero_dir = output_file.mkdir('antidelta_zero')
antideltazero_dir.mkdir('same-event')
antideltazero_dir.mkdir('mixed-event')
antideltazero_dir.mkdir('comp')
antideltazero_dir.mkdir('diff')
if mc:
    antideltazero_dir.mkdir('generated')

print('AntiDelta0')
createHistograms(label='AntiDeltaZero', res_dir=antideltazero_dir)
