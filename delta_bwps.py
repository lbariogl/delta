import ROOT
import argparse
import yaml
import math

kBlueC = ROOT.TColor.GetColor('#1f78b4')
kOrangeC = ROOT.TColor.GetColor('#ff7f00')
ROOT.gROOT.SetBatch()
# silent mode for fits
ROOT.RooMsgService.instance().setSilentMode(True)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
ROOT.gROOT.LoadMacro(r'RooCustomPdfs/RooBWPS.cxx++')
# ROOT.gROOT.LoadMacro('RooCustomPdfs/RooVoigtianExp.cxx++')

parser = argparse.ArgumentParser(
    description='Configure the parameters of the script.')
parser.add_argument('--mc', dest='mc', action='store_true',
                    help="if True MC information is stored.", default=False)
parser.add_argument('--config-file', dest='config_file',
                    help="path to the YAML file with configuration.", default='delta_fit_parameters.yaml')
args = parser.parse_args()
if args.config_file == "":
    print('** No config file provided. Exiting. **')
    exit()

mc = args.mc

delta_params_file = open(args.config_file, 'r')
delta_params = yaml.full_load(delta_params_file)


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

    hChi2Pt = histo_2D_SE.ProjectionX("hChi2pT")
    hChi2Pt.GetYaxis().SetTitle(r'#chi^{2} / NDF')
    hChi2Pt.GetYaxis().SetTitleOffset(1.2)
    hChi2Pt.SetTitle('')
    hRawSpectrum = hChi2Pt.Clone('hRawSpectrum')
    hRawSpectrum.GetYaxis().SetTitle(
        r'#frac{d#it{N}}{d#it{p}_{T}} (GeV/#it{c})^{-1}')
    hRawSpectrum.GetYaxis().SetTitleOffset(1.2)
    hRawSpectrum.SetTitle('')

    for i_pt in range(1, histo_2D_SE.GetXaxis().GetNbins() + 1):
        print(f'pt bin {i_pt} / {histo_2D_SE.GetXaxis().GetNbins()}')
        pt_title = f'{label} ' + str(histo_2D_SE.GetXaxis().GetBinLowEdge(i_pt)) + r' #leq #it{p}_{T} < ' + str(
            histo_2D_SE.GetXaxis().GetBinLowEdge(i_pt + 1)) + r' (GeV/#it{c})'
        pt_centre = histo_2D_SE.GetXaxis().GetBinCenter(i_pt)
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
        first_scale_bin = histo_SE.FindBin(1.5+epsilon)
        last_scale_bin = histo_SE.FindBin(1.8-epsilon)
        scale_factor = histo_SE.Integral(
            first_scale_bin, last_scale_bin) / histo_ME.Integral(first_scale_bin, last_scale_bin)
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
        mass = ROOT.RooRealVar('m', 'm', 1.05, 1.8, 'GeV/c^{2}')

        # signal
        m0 = ROOT.RooRealVar(
            'm0', r'm_{0}', 1.2, 1.4, r'GeV/#it{c}^{2}')
        gamma = ROOT.RooRealVar(
            'gamma', r'#Gamma', 0.1, 0.13, r'GeV/#it{c}^{2}')
        pt = ROOT.RooRealVar(
            'pt', r'#it{p}_{T}', 0.1, 10, r'GeV/#it{c}')
        pt.setVal(pt_centre)
        pt.setConstant(True)
        temp = ROOT.RooRealVar(
            'temp', 'T', 0.150, 0.160, 'GeV')


        # signal = ROOT.RooVoigtianExp(
        #     'voigt_exp', 'voigt_exp', mass, m0, gamma, gamma, tau, True)

        signal = ROOT.RooBWPS(
            'bwps', 'bwps signal', mass, m0, gamma, pt, temp)
        # background
        c0 = ROOT.RooRealVar(
            'c0', 'constant c0', delta_params['c0_low'][i_pt-1], delta_params['c0_up'][i_pt-1])

        background = ROOT.RooChebychev(
            'bkg', 'pol1 bkg', mass, ROOT.RooArgList(c0))

        # total
        n_signal = ROOT.RooRealVar(
            'n_signal', 'n_signal', delta_params['n_signal_low'][i_pt-1], delta_params['n_signal_up'][i_pt-1])
        n_background = ROOT.RooRealVar(
            'n_background', 'n_background', delta_params['n_background_low'][i_pt-1], delta_params['n_background_up'][i_pt-1])

        model = ROOT.RooAddPdf('total_pdf', 'signal + background', ROOT.RooArgList(
            signal, background), ROOT.RooArgList(n_signal, n_background))

        rooMass_diff = ROOT.RooDataHist(f'rooMass_{i_pt}', pt_title, ROOT.RooArgList(
            mass), ROOT.RooFit.Import(histo_diff, False))
        fit_results = model.fitTo(rooMass_diff, ROOT.RooFit.Save(
            True), ROOT.RooFit.Verbose(False))

        # retrieve parameteres from fit
        frame = mass.frame()
        frame.SetName(f'f{label}_diff_{i_pt}')
        frame.SetTitle(pt_title)
        rooMass_diff.plotOn(frame, ROOT.RooFit.Name('data'), ROOT.RooFit.DrawOption(
            'pz'), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
        model.plotOn(frame, ROOT.RooFit.Components('bkg'), ROOT.RooFit.LineStyle(
            ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed+1))
        model.plotOn(frame, ROOT.RooFit.LineColor(
            ROOT.kAzure+1), ROOT.RooFit.Name('total_pdf'))

        chi2 = frame.chiSquare('total_pdf', 'data')
        ndf = histo_2D_SE.GetYaxis().GetNbins() - fit_results.floatParsFinal().getSize()

        # add pave for stats
        pinfo_vals = ROOT.TPaveText(0.632, 0.5, 0.932, 0.85, 'NDC')
        pinfo_vals.SetBorderSize(0)
        pinfo_vals.SetFillStyle(0)
        pinfo_vals.SetTextAlign(11)
        pinfo_vals.SetTextFont(42)
        pinfo_vals.AddText(
            'm_{0} = ' + f'{m0.getVal():.3f} #pm {m0.getError():.3f}' + r' GeV/#it{c}^{2}')
        # pinfo_vals.AddText(
        #     '#Gamma = ' + f'{gamma.getVal():.3f} #pm {gamma.getError():.3f}' + ' GeV/#it{c}^{2}')
        pinfo_vals.AddText(
            '#Gamma = ' + f'{gamma.getVal():.3f} #pm {gamma.getError():.3f}' + r' GeV/#it{c}^{2}')
        pinfo_vals.AddText(
            'temp = ' + f'{temp.getVal():.3f} #pm {temp.getError():.3f}' + ' GeV')
        pinfo_vals.AddText(
            'N_{signal} = ' + f'{n_signal.getVal():.0f} #pm {n_signal.getError():.0f}')
        pinfo_vals.AddText(
            'c_{0} = ' + f'{c0.getVal():.3f} #pm {c0.getError():.3f}')
        pinfo_vals.AddText(
            'N_{background} = ' + f'{n_background.getVal():.0f} #pm {n_background.getError():.0f}')
        pinfo_vals.AddText(
            '#chi^{2} / NDF = ' + f'{chi2:.3f} (NDF: {ndf})')
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

        if not math.isnan(chi2):
            hChi2Pt.SetBinContent(i_pt, chi2)
            hChi2Pt.SetBinError(i_pt, 0)
        print(f'i_pt: {i_pt} chi2 : {chi2}')
        hRawSpectrum.SetBinContent(i_pt, n_signal.getVal())
        hRawSpectrum.SetBinError(i_pt, n_signal.getError())

    res_dir.cd('Pt')
    hChi2Pt.SetMarkerStyle(20)
    cChi2Pt = ROOT.TCanvas("cChi2Pt", "cChi2Pt", 800, 600)
    cChi2Pt.SetLeftMargin(0.15)
    hChi2Pt.Draw()
    cChi2Pt.SetLogy()
    cChi2Pt.Write()
    hRawSpectrum.SetMarkerStyle(20)
    cRawSpectrum = ROOT.TCanvas("cRawSpectrum", "cRawSpectrum", 800, 600)
    cRawSpectrum.SetLeftMargin(0.15)
    hRawSpectrum.Draw("PE")
    cRawSpectrum.Write()

    if mc:
        return hMass, hMass_EM, hMass_diff, hMass_Gen, cComp
    else:
        return hMass, hMass_EM, hMass_diff, cComp


# input
input_file = ROOT.TFile.Open('mc/AnalysisResults_train.root')
input_dir = input_file.Get('deltaAnalysis')

# output
output_file = ROOT.TFile('delta_bwps.root', 'recreate')

# Delta++
deltaplusplus_dir = output_file.mkdir('delta_plusplus')
deltaplusplus_dir.mkdir('same-event')
deltaplusplus_dir.mkdir('mixed-event')
deltaplusplus_dir.mkdir('comp')
deltaplusplus_dir.mkdir('diff')
if mc:
    deltaplusplus_dir.mkdir('generated')

deltaplusplus_dir.mkdir('Pt')

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

antideltaplusplus_dir.mkdir('Pt')

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

deltazero_dir.mkdir('Pt')

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

antideltazero_dir.mkdir('Pt')

print('AntiDelta0')
createHistograms(label='AntiDeltaZero', res_dir=antideltazero_dir)
