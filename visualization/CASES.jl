# load libraries
using DifferentialEquations, CSV, DelimitedFiles,DataFrames


# ODE function
function cases6_ages!(du,u,p,t)

    b,g,l = p
    n = [0.00004,0.000047,0.000101,0.000186]
    d = [0.002,0.0027,0.0295,0.088]

    # calculate mu term
    m = Array{Float64}(undef, no_sectors)
    for i = 1:no_sectors
        mu = 0.0
        for j = 1:no_sectors
            mu = mu + (M[i,j]*u[j]/E[j])
        end
        m[i] = mu
    end

    D = Float64[]
    for i = 1:4
        push!(D,(l*(d[i]+n[i]))*u[77])
    end

    du[1] = u[1]*(-1.0*D[1])*(A[1,1]+m[1])
    du[2] = u[2]*(-1.0*D[2])*(A[1,1]+m[1])
    du[3] = u[3]*(-1.0*D[3])*(A[1,1]+m[1])
    du[4] = u[4]*(-1.0*D[4])*(A[1,1]+m[1])

    du[5] = u[5]*(-1.0*D[1])*(A[2,2]+m[2])
    du[6] = u[6]*(-1.0*D[2])*(A[2,2]+m[2])
    du[7] = u[7]*(-1.0*D[3])*(A[2,2]+m[2])
    du[8] = u[8]*(-1.0*D[4])*(A[2,2]+m[2])

    du[9] = u[9]*(-1.0*D[1])*(A[3,3]+m[3])
    du[10] = u[19]*(-1.0*D[2])*(A[3,3]+m[3])
    du[11] = u[11]*(-1.0*D[3])*(A[3,3]+m[3])
    du[12] = u[12]*(-1.0*D[4])*(A[3,3]+m[3])

    du[13] = u[13]*(-1.0*D[1])*(A[4,4]+m[4])
    du[14] = u[14]*(-1.0*D[2])*(A[4,4]+m[4])
    du[15] = u[15]*(-1.0*D[3])*(A[4,4]+m[4])
    du[16] = u[16]*(-1.0*D[4])*(A[4,4]+m[4])

    du[17] = u[17]*(-1.0*D[1])*(A[5,5]+m[5])
    du[18] = u[18]*(-1.0*D[2])*(A[5,5]+m[5])
    du[19] = u[19]*(-1.0*D[3])*(A[5,5]+m[5])
    du[20] = u[20]*(-1.0*D[4])*(A[5,5]+m[5])

    du[21] = u[21]*(-1.0*D[1])*(A[6,6]+m[6])
    du[22] = u[22]*(-1.0*D[2])*(A[6,6]+m[6])
    du[23] = u[23]*(-1.0*D[3])*(A[6,6]+m[6])
    du[24] = u[24]*(-1.0*D[4])*(A[6,6]+m[6])

    du[25] = u[25]*(-1.0*D[1])*(A[7,7]+m[7])
    du[26] = u[26]*(-1.0*D[2])*(A[7,7]+m[7])
    du[27] = u[27]*(-1.0*D[3])*(A[7,7]+m[7])
    du[28] = u[28]*(-1.0*D[4])*(A[7,7]+m[7])

    du[29] = u[29]*(-1.0*D[1])*(A[8,8]+m[8])
    du[30] = u[30]*(-1.0*D[2])*(A[8,8]+m[8])
    du[31] = u[31]*(-1.0*D[3])*(A[8,8]+m[8])
    du[32] = u[32]*(-1.0*D[4])*(A[8,8]+m[8])

    du[33] = u[33]*(-1.0*D[1])*(A[9,9]+m[9])
    du[34] = u[34]*(-1.0*D[2])*(A[9,9]+m[9])
    du[35] = u[35]*(-1.0*D[3])*(A[9,9]+m[9])
    du[36] = u[36]*(-1.0*D[4])*(A[9,9]+m[9])

    du[37] = u[37]*(-1.0*D[1])*(A[10,10]+m[10])
    du[38] = u[38]*(-1.0*D[2])*(A[10,10]+m[10])
    du[39] = u[39]*(-1.0*D[3])*(A[10,10]+m[10])
    du[40] = u[40]*(-1.0*D[4])*(A[10,10]+m[10])

    du[41] = u[41]*(-1.0*D[1])*(A[11,11]+m[11])
    du[42] = u[42]*(-1.0*D[2])*(A[11,11]+m[11])
    du[43] = u[43]*(-1.0*D[3])*(A[11,11]+m[11])
    du[44] = u[44]*(-1.0*D[4])*(A[11,11]+m[11])

    du[45] = u[45]*(-1.0*D[1])*(A[12,12]+m[12])
    du[46] = u[46]*(-1.0*D[2])*(A[12,12]+m[12])
    du[47] = u[47]*(-1.0*D[3])*(A[12,12]+m[12])
    du[48] = u[48]*(-1.0*D[4])*(A[12,12]+m[12])

    du[49] = u[49]*(-1.0*D[1])*(A[13,13]+m[13])
    du[50] = u[50]*(-1.0*D[2])*(A[13,13]+m[13])
    du[51] = u[51]*(-1.0*D[3])*(A[13,13]+m[13])
    du[52] = u[52]*(-1.0*D[4])*(A[13,13]+m[13])

    du[53] = u[53]*(-1.0*D[1])*(A[14,14]+m[14])
    du[54] = u[54]*(-1.0*D[2])*(A[14,14]+m[14])
    du[55] = u[55]*(-1.0*D[3])*(A[14,14]+m[14])
    du[56] = u[56]*(-1.0*D[4])*(A[14,14]+m[14])

    du[57] = u[57]*(-1.0*D[1])*(A[15,15]+m[15])
    du[58] = u[58]*(-1.0*D[2])*(A[15,15]+m[15])
    du[59] = u[59]*(-1.0*D[3])*(A[15,15]+m[15])
    du[60] = u[60]*(-1.0*D[4])*(A[15,15]+m[15])

    du[61] = du[1] + du[2] + du[3] + du[4]
    du[62] = du[5] + du[6] + du[7] + du[8]
    du[63] = du[9] + du[10] + du[11] + du[12]
    du[64] = du[13] + du[14] + du[15] + du[16]
    du[65] = du[17] + du[18] + du[19] + du[20]
    du[66] = du[21] + du[22] + du[23] + du[24]
    du[67] = du[25] + du[26] + du[27] + du[28]
    du[68] = du[29] + du[30] + du[31] + du[32]
    du[69] = du[33] + du[34] + du[35] + du[36]
    du[70] = du[37] + du[38] + du[39] + du[40]
    du[71] = du[41] + du[42] + du[43] + du[44]
    du[72] = du[45] + du[46] + du[47] + du[48]
    du[73] = du[49] + du[50] + du[51] + du[52]
    du[74] = du[53] + du[54] + du[55] + du[56]
    du[75] = du[57] + du[58] + du[59] + du[60]

    # SIR calculation
    du[76] = -b*u[76]*u[77]
    du[77] = (b*u[76]*u[77])-(g*u[77])
    du[78] = g*u[77]
end


function main(I,age_fracs,employed)
    println("Starting Julia calculation...")
    # the input-output matrix
    # reading a delimited file

    # **********************************************************
    # HARD CODED UNIQUE FILE
    # input employment data
    N = sum(employed[:,:Feb])
    # **********************************************************

    # calculate alpha, beta and gamma coefficient
    global no_sectors = size(I,1)

    # beta and gamma matrices
    global A = Array{Float64}(undef,no_sectors,no_sectors)
    global B = Array{Float64}(undef,no_sectors,no_sectors)
    global C = Array{Float64}(undef,no_sectors,no_sectors)
    abc = Float64[]
    for i = 1:no_sectors
        row_sum = 0.0
        for j = 1:no_sectors
            row_sum = row_sum +I[i,j] + I[j,i]
        end
        row_sum = row_sum - I[i,i]
        push!(abc,row_sum)
    end

    for i = 1:no_sectors
        #abc = sum(I[:,1])+sum(I[1,:])-(I[1,1])
        for j = 1:no_sectors
            A[i,j] = 0.0
            B[i,j] = I[j,i]/abc[i]
            C[i,j] = I[i,j]/abc[i]
        end
        A[i,i] = I[i,i]/abc[i]
        B[i,i] = 0.0
        C[i,i] = 0.0
    end

    # calculate mu matrix (beta+gamma)
    global M = B + C;

    # **********************************************************
    # HARD CODED UNIQUE FILE
    # Arrays for employment and initial levels
    # **********************************************************
    # age bracket sizes
    age_sizes = Float64[]
    for i = 1:4
        age_size = 0.0
        for j = 1:size(employed,1)
            age_size = age_size + (age_fracs[j,i]*convert(Float64,employed[j,:Feb]))
        end
        push!(age_sizes,age_size)
    end

    # Arrays for employment and initial levels
    global E = Float64[]
    u0 = Float64[]
    for i = 1:no_sectors
        push!(E,convert(Float64,employed[i,:Feb]))
        for j = 1:4
            push!(u0,age_fracs[i,j]*convert(Float64,employed[i,:Feb]))
        end
    end
    for i = 1:no_sectors
        push!(u0,convert(Float64,employed[i,:Feb]))
    end
    # add the S, I and R values, normalized by total population size
    push!(u0,0.999998)
    push!(u0,0.000002)
    push!(u0,0.0)

    # **********************************************************
    # HARD CODED UNIQUE FILE
    # open output file
    rows = 511
    # Joe: These should be vectors of arrays instead of hardcoded length 2d arrays
    one_d_array = Array{Float64,1}

    global io1a = Array{one_d_array,1}()
    global io2a = Array{one_d_array,1}()
    #global io1a = Array{Float64}(undef,rows,81)
    #global io2a = Array{Float64}(undef,77162,4)
    io1 = open("LA_CASES6_output_08_25.dat", "w");
    #io2 = open("LA_CASES6_surfaces_08_25.dat","w");
    # **********************************************************

    # write column headers
    print(io1,"R,Day Farm_1,Farm_2,Farm_3,Farm_4,Mining_1,Mining_2,Mining_3,Mining_4,Utilities_1,Utilities_2,Utilities_3,Utilities_4,Construction_1,Construction_2,Construction_3,Construction_4,Manf_1,Manf_2,Manf_3,Manf_4,Wholesale_1,Wholesale_2,Wholesale_3,Wholesale_4,Retail_1,Retail_2,Retail_3,Retail_4,Transp_1,Transp_2,Transp_3,Transp_4,Information_1,Information_2,Information_3,Information_4,Financial_1,Financial_2,Financial_3,Financial_4,Prof_1,Prof_2,Prof_3,Prof_4,Ed_Hlth_1,Ed_Hlth_2,Ed_Hlth_3,Ed_Hlth_4,Leisure_1,Leisure_2,Leisure_3,Leisure_4,Other_1,Other_2,Other_3,Other_4,Gov_1,Gov_2,Gov_3,Gov_4,Farm,Mining,Utilities,Construction,Manf,Wholesale,Retail,Transp,Information,Financial,Prof,Ed_Hlth,Leisure,Other,Gov,Susceptible,Infected,Removed,total_E,Disease_only\n")

    # begin simulation set
    for i = 1:rows

        # parameters
        R = 0.89 + (i*.01)
        beta = 0.07*R

        p = [beta,0.07,0.453];
        n = [0.00004,0.000047,0.000101,0.000186];
        d = [0.002,0.0027,0.0295,0.088];

        #println("R0 = ",R)

        # solve ODE system
        # we run it here for 150 days
        tspan = (0.0,150.0)
        prob1 = ODEProblem(cases6_ages!,u0,tspan,p)
        sol1=solve(prob1,saveat=1.0);

        # summarize SIR and employment and write to output file
        total_E1 = Array(sol1)

        for j = 1:size(total_E1,2)
            cur_array_1 = one_d_array()

            push!(cur_array_1,R)
            push!(cur_array_1,j)

            print(io1,R,",",j,",")
            for k = 1:size(total_E1,1)
                print(io1,total_E1[k,j],",")
                push!(cur_array_1,total_E1[k,j])

                # io1a[i,k+2]=j
            end
            print(io1,"\n")
            push!(io1a,cur_array_1)

        end


        # data processing for surfaces
        for j = 1:size(total_E1,2)
            cur_array_2 = one_d_array()
            total_E = 0.0
            for k = 61:75
                # employment
                total_E = total_E + total_E1[k,j]
            end
            #print(io2,R," ",j," ",total_E," ")
            #io2a[j,1]=R
            #io2a[j,2]=j
            #io2a[j,3]=total_E
            cur_array_2=[R,j,total_E]

            # removed
            age1 = age_sizes[1] - (total_E1[78,j]*age_sizes[1]*(d[1]+n[1]))
            age2 = age_sizes[2] - (total_E1[78,j]*age_sizes[2]*(d[2]+n[2]))
            age3 = age_sizes[3] - (total_E1[78,j]*age_sizes[3]*(d[3]+n[3]))
            age4 = age_sizes[4] - (total_E1[78,j]*age_sizes[4]*(d[4]+n[4]))
            disease_only = age1 + age2 + age3 + age4
            #print(io2,disease_only,"\n")
            #io2a[j,4]=disease_only
            push!(cur_array_2,disease_only)
            #println("Pushed: ",R," ",j," ",total_E," ",disease_only)
            #println(cur_array_2)
            push!(io2a,cur_array_2)

        end

        #println(io2a,"\n")
        #println("Cur outer loop: ",i)

    end

    # close output file
    close(io1)
    #close(io2)
    io1a,io2a
end

#
# Uncomment for standalone run. Leave commented for python run.
#
#age_fracs = readdlm("LA_age_fracs.csv")
#employed = DataFrame!(CSV.File("LA_employment_by_sector_02_2020.csv"))
#I = readdlm("US_exchanges_2018c.csv")
#main(I,age_fracs,employed)
