import ROOT

input_file = ROOT.TFile.Open('delta.root')

canvas = ROOT.TCanvas("canvas")
canvas.SaveAs("fit_delta.pdf[")
canvas.Clear()

i_pts = list(range(1,20))
for i_pt in i_pts:
    HISTO_FIT = input_file.Get(f'delta_plusplus/diff/fDeltaPlusPlus_diff_{i_pt}')
    HISTO_FIT.Draw()
    canvas.SaveAs("fit_delta.pdf")
    canvas.Clear()

for i_pt in i_pts:
    HISTO_FIT = input_file.Get(f'antidelta_plusplus/diff/fAntiDeltaPlusPlus_diff_{i_pt}')
    HISTO_FIT.Draw()
    canvas.SaveAs("fit_delta.pdf")
    canvas.Clear()

for i_pt in i_pts:
    HISTO_FIT = input_file.Get(f'delta_zero/diff/fDeltaZero_diff_{i_pt}')
    HISTO_FIT.Draw()
    canvas.SaveAs("fit_delta.pdf")
    canvas.Clear()

for i_pt in i_pts:
    HISTO_FIT = input_file.Get(f'antidelta_zero/diff/fAntiDeltaZero_diff_{i_pt}')
    HISTO_FIT.Draw()
    canvas.SaveAs("fit_delta.pdf")
    canvas.Clear()


canvas.SaveAs("fit_delta.pdf]")


"""

label1s = ['delta_plusplus', 'antidelta_plusplus', 'delta_zero', 'antidelta_zero']

for label1 in label1s:

    input_dir = input_file.Get(f'{label1}/diff')


    label2s = ['DeltaPlusPlus', 'AntiDeltaPlusPlus', 'DeltaZero', 'AntiDeltaZero']

    for label2 in label2s:
        i_pts = list(range(1,20))
        for i_pt in i_pts:

            HISTO_FIT_i_pt = input_dir.Get(f'f{label2}_diff_{i_pt}')
            print(f'f{label2}_diff_{i_pt}')

            HISTO_FIT.Draw()
            canvas.SaveAs("my_output.pdf")  
            canvas.Clear()


canvas.SaveAs("my_output.pdf]")

"""

