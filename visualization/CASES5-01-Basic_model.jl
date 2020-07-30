using StatsPlots, DelimitedFiles, CSV, Plots, DataFrames
# reading a delimited file
I = readdlm("US_exchanges_2018c.csv")

# load dataset
employed = CSV.read("LA_employment_by_sector_2020.csv")

no_sectors = size(I,1)

# beta and gamma matrices
A = Array{Float64}(undef,no_sectors,no_sectors)
B = Array{Float64}(undef,no_sectors,no_sectors)
C = Array{Float64}(undef,no_sectors,no_sectors)
abc = Float64[]
for i = 1:no_sectors
    row_sum = 0.0
    for j = 1:no_sectors
        row_sum = row_sum +I[i,j] + I[j,i]
    end
    row_sum = row_sum - I[i,i]
    push!(abc,row_sum)
end
#print(abc)

        
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

# parameter array
p = Array{Float64}(undef,no_sectors,3)
for i = 1:no_sectors
    p[i,1] = (employed[i,:Mar] - employed[i,:Feb])/(employed[i,:Feb]*30)
    p[i,2] = 0.0
    p[i,3] = 0.0
end

# perturbation
D = Float64[]
for i = 1:no_sectors
    push!(D,p[i,1]+p[i,2]+p[i,3])
end
#print(D)

# time
T = 30

# employment
E = Array{Float64}(undef,T,no_sectors+1)
U = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
for i = 1:no_sectors
    E[1,1] = 1.0
    E[1,i+1] = employed[i,:Mar]
    U[1,1] = 1.0
    U[1,i+1] = 0.0
end

# simulate
for i = 2:T
    E[i,1] = convert(Float64,i)
    for j = 1:no_sectors
        alpha = A[j,j]*(1.0+D[j])*E[i-1,j+1]/E[1,j+1]
        #println(alpha)
        beta = 0.0
        for k = 1:no_sectors
            beta = beta + ((1.0+D[k])*(B[j,k]+C[j,k])*(E[i-1,k+1]/E[1,k+1]))
        end
        #println(beta)
        a = alpha+beta
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(E[i-1,j+1]) - E[i-1,j+1])
            #println(del_E)
            if del_E <= U[i-1,j+1] # if re-hiring possible
                E[i,j+1] = round(a*E[i-1,j+1]) #+ del_E
                U[i,j+1] = round((U[i-1,j+1]*(1-p[2])) + ((E[i-1,j+1]-E[i,j+1])))*(1-p[2])
            elseif del_E > U[i-1,j+1]
                E[i,j+1] = E[i-1,j+1] + U[i-1,j+1]
                U[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = E[i-1,j+1] - round(a*(E[i-1,j+1]))
            E[i,j+1] = round(a*(E[i-1,j+1]))
            U[i,j+1] = U[i-1,j+1]*(1-p[2]) + (E[i-1,j+1]-E[i,j+1])
        end
        # no negative unemployment
        if U[i,j+1] < 0.0
            U[i,j+1] = 0.0
        end
        if U[i,j+1] >= E[1,j+1]
            U[i,j+1] = E[1,j+1]
        end
    end
end
#print(E)

# plot
e = Float64[]
u = Float64[]
for i = 1:T
    push!(e,sum(E[i,:])-E[i,1])
    push!(u,sum(U[i,:])-U[i,1])
end
plot(e,xlabel="t",ylabel="Total employment",label="Employed",lw=2)
plot!(u,label="Unemployed",lw=2)

# parameter array
p = Array{Float64}(undef,no_sectors,3)
for i = 1:no_sectors
    p[i,1] = (employed[i,:Mar] - employed[i,:Feb])/(employed[i,:Feb]*30)
    #p[i,1] = 0.1
    p[i,2] = 0.0
    p[i,3] = 0.0
end

# perturbation
D = Float64[]
for i = 1:no_sectors
    push!(D,p[i,1]+p[i,2]+p[i,3])
end
#print(D)

Ei = Array{Float64}(undef,T,no_sectors+1)
Ui = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
for i = 1:no_sectors
    Ei[1,1] = 1.0
    Ei[1,i+1] = employed[i,:Mar]
    Ui[1,1] = 1.0
    Ui[1,i+1] = 0.0
end
for i = 2:T
    Ei[i,1] = convert(Float64,i)
    for j = 1:no_sectors
        alpha = (Ei[i-1,j+1])*(1.0+D[j])/Ei[1,j+1]
        a = alpha
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(Ei[i-1,j+1]) - Ei[i-1,j+1])
            #println(del_E)
            if del_E <= Ui[i-1,j+1] # if re-hiring possible
                Ei[i,j+1] = round(a*Ei[i-1,j+1]) #+ del_E
                Ui[i,j+1] = round((Ui[i-1,j+1]*(1-p[2])) + (Ei[i-1,j+1]-Ei[i,j+1]))
            elseif del_E > Ui[i-1,j+1]
                Ei[i,j+1] = Ei[i-1,j+1] + Ui[i-1,j+1]
                Ui[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = Ei[i-1,j+1] - round(a*(Ei[i-1,j+1]))
            Ei[i,j+1] = round(a*(Ei[i-1,j+1]))
            Ui[i,j+1] = Ui[i-1,j+1]*(1-p[2]) + (Ei[i-1,j+1]-Ei[i,j+1])
        end
        # no negative unemployment
        if Ui[i,j+1] < 0.0
            Ui[i,j+1] = 0.0
        end
        if Ui[i,j+1] >= Ei[1,j+1]
            Ui[i,j+1] = Ei[1,j+1]
        end
    end
end
#print(E)

# plot
ei = Float64[]
ui = Float64[]
for i = 1:T
    push!(ei,sum(Ei[i,:])-Ei[i,1])
    push!(ui,sum(Ui[i,:])-Ui[i,1])
end
plot(ei,xlabel="t",ylabel="Total employment",label="independent model",lw=2)
plot!(e,lw=2,label="basic model")

# parameter array
p = Array{Float64}(undef,no_sectors,3)
for i = 1:no_sectors
    p[i,1] = 0.0
    if employed[i,:Sector]=="Wholesale trade"
        p[i,1] = (employed[i,:Mar] - employed[i,:Feb])/(employed[i,:Feb]*30)
       # p[i,1] = -0.0002
    end
    p[i,2] = 0.0
    p[i,3] = 0.0
end

# perturbation
Dm = Float64[]
for i = 1:no_sectors
    push!(Dm,p[i,1]+p[i,2]+p[i,3])
end
#print(Dm)

# time
T = 30

# employment
Em = Array{Float64}(undef,T,no_sectors+1)
Um = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
for i = 1:no_sectors
    Em[1,1] = 1.0
    Em[1,i+1] = employed[i,:Mar]
    Um[1,1] = 1.0
    Um[1,i+1] = 0.0
end

# simulate
for i = 2:T
    Em[i,1] = convert(Float64,i)
    for j = 1:no_sectors
        alpha = A[j,j]*(1.0+Dm[j])*Em[i-1,j+1]/Em[1,j+1]
        #println(alpha)
        beta = 0.0
        for k = 1:no_sectors
            beta = beta + ((1.0+Dm[k])*(B[j,k]+C[j,k])*(Em[i-1,k+1]/Em[1,k+1]))
        end
        #println(beta)
        a = alpha+beta
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(Em[i-1,j+1]) - Em[i-1,j+1])
            #println(del_E)
            if del_E <= Um[i-1,j+1] # if re-hiring possible
                Em[i,j+1] = round(a*Em[i-1,j+1]) #+ del_E
                Um[i,j+1] = round((Um[i-1,j+1]*(1-p[2])) + ((Em[i-1,j+1]-Em[i,j+1])))*(1-p[2])
            elseif del_E > Um[i-1,j+1]
                Em[i,j+1] = Em[i-1,j+1] + Um[i-1,j+1]
                Um[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = Em[i-1,j+1] - round(a*(Em[i-1,j+1]))
            Em[i,j+1] = round(a*(Em[i-1,j+1]))
            Um[i,j+1] = Um[i-1,j+1]*(1-p[2]) + (Em[i-1,j+1]-Em[i,j+1])
        end
        # no negative unemployment
        if Um[i,j+1] < 0.0
            Um[i,j+1] = 0.0
        end
        if Um[i,j+1] >= Em[1,j+1]
            Um[i,j+1] = Em[1,j+1]
        end
    end
end
#print(E)

# plot
em = Float64[]
um = Float64[]
for i = 1:T
    push!(em,sum(Em[i,:])-Em[i,1])
    push!(um,sum(Um[i,:])-Um[i,1])
end
#plot(em,xlabel="t",ylabel="Total employment",label="Employed",lw=2)
#plot!(um,label="Unemployed",lw=2)

# parameter array
p = Array{Float64}(undef,no_sectors,3)
for i = 1:no_sectors
    p[i,1] = 0.0
    if employed[i,:Sector]=="Leisure and hospitality"
        p[i,1] = (employed[i,:Mar] - employed[i,:Feb])/(employed[i,:Feb]*30)
        #p[i,1] = -0.0002
    end
    p[i,2] = 0.0
    p[i,3] = 0.0
end

# perturbation
Dl = Float64[]
for i = 1:no_sectors
    push!(Dl,p[i,1]+p[i,2]+p[i,3])
end
#print(Dl)

# time
T = 30

# employment
El = Array{Float64}(undef,T,no_sectors+1)
Ul = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
for i = 1:no_sectors
    El[1,1] = 1.0
    El[1,i+1] = employed[i,:Mar]
    Ul[1,1] = 1.0
    Ul[1,i+1] = 0.0
end

# simulate
for i = 2:T
    El[i,1] = convert(Float64,i)
    for j = 1:no_sectors
        alpha = A[j,j]*(1.0+Dl[j])*El[i-1,j+1]/El[1,j+1]
        #println(alpha)
        beta = 0.0
        for k = 1:no_sectors
            beta = beta + ((1.0+Dl[k])*(B[j,k]+C[j,k])*(El[i-1,k+1]/El[1,k+1]))
        end
        #println(beta)
        a = alpha+beta
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(El[i-1,j+1]) - El[i-1,j+1])
            #println(del_E)
            if del_E <= Ul[i-1,j+1] # if re-hiring possible
                El[i,j+1] = round(a*El[i-1,j+1]) #+ del_E
                Ul[i,j+1] = round((Ul[i-1,j+1]*(1-p[2])) + ((El[i-1,j+1]-El[i,j+1])))*(1-p[2])
            elseif del_E > Ul[i-1,j+1]
                El[i,j+1] = El[i-1,j+1] + Ul[i-1,j+1]
                Ul[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = El[i-1,j+1] - round(a*(El[i-1,j+1]))
            El[i,j+1] = round(a*(El[i-1,j+1]))
            Ul[i,j+1] = Ul[i-1,j+1]*(1-p[2]) + (El[i-1,j+1]-El[i,j+1])
        end
        # no negative unemployment
        if Ul[i,j+1] < 0.0
            Ul[i,j+1] = 0.0
        end
        if Ul[i,j+1] >= El[1,j+1]
            Ul[i,j+1] = El[1,j+1]
        end
    end
end
#print(E)

# plot
el = Float64[]
ul = Float64[]
for i = 1:T
    push!(el,sum(El[i,:])-El[i,1])
    push!(ul,sum(Ul[i,:])-Ul[i,1])
end
#plot(el,xlabel="t",ylabel="Total employment",label="Employed",lw=2)
#plot!(ul,label="Unemployed",lw=2)

plot(em,xlabel="t",ylabel="Total employment",label="Wholesale trade",lw=2)
plot!(el,lw=2,label="Leisure and hospitality")

# parameter array
# reverse signs of previous parameter values
p = Array{Float64}(undef,no_sectors,3)
for i = 1:no_sectors
    #p[i,1] = 36.18*abs(employed[i,:Feb] - employed[i,:Jan])/(employed[i,:Jan]*1)
    p[i,1] = 1*(employed[i,:Mar] - employed[i,:Feb])/(employed[i,:Feb]*1)
    if p[i,1] > 0
        p[i,1] = 0.0
    end
    p[i,2] = 0.0
    p[i,3] = 0.0
end

# perturbation
D = Float64[]
for i = 1:no_sectors
    push!(D,p[i,1]+p[i,2]+p[i,3])
end
#print(D)

# time
T = 30

# employment
E2 = Array{Float64}(undef,T,no_sectors+1)
U2 = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
# reverse time
# use Day xx from previous simulation
for i = 1:no_sectors
    E2[1,1] = 11.0
    E2[1,i+1] = E[11,i+1]
    U2[1,1] = 11.0
    U2[1,i+1] = U[10,i+1]
end

# simulate
for i = 2:T
    E2[i,1] = 12.0 - convert(Float64,i)
    U2[i,1] = 12.0 - convert(Float64,i)
    for j = 1:no_sectors
        alpha = A[j,j]*(1.0+D[j])*E2[i-1,j+1]/E[1,j+1]
        #println(alpha)
        beta = 0.0
        for k = 1:no_sectors
            beta = beta + ((1.0+D[k])*(B[j,k]+C[j,k])*(E2[i-1,k+1]/E[1,k+1]))
        end
        #println(beta)
        a = alpha+beta
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(E2[i-1,j+1]) - E2[i-1,j+1])
            #println(del_E)
            if del_E <= U2[i-1,j+1] # if re-hiring possible
                E2[i,j+1] = round(a*E2[i-1,j+1]) #+ del_E
                U2[i,j+1] = round((U2[i-1,j+1]*(1-p[2])) + ((E2[i-1,j+1]-E2[i,j+1]))*(1-p[2]))
            elseif del_E > U2[i-1,j+1]
                E2[i,j+1] = E2[i-1,j+1] + U2[i-1,j+1]
                U2[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = E2[i-1,j+1] - round(a*(E2[i-1,j+1]))
            E2[i,j+1] = round(a*(E2[i-1,j+1]))
            U2[i,j+1] = U2[i-1,j+1]*(1-p[2]) + (E2[i-1,j+1]-E2[i,j+1])
        end
        # no negative unemployment
        if U2[i,j+1] < 0.0
            U2[i,j+1] = 0.0
        end
        if U2[i,j+1] >= E2[1,j+1]
            U2[i,j+1] = E2[1,j+1]
        end
    end
end
#print(E2)

# plot
e2 = Float64[]
u2 = Float64[]
for i = 1:T
    push!(e2,sum(E2[i,:])-E2[i,1])
    push!(u2,sum(U2[i,:])-U2[i,1])
end
plot(e,xlabel="t",ylabel="Total employment",label="basic model",lw=2)
plot!(e2,lw=2,label="recovery")
#plot!(u2)

e10 = [2.75013e6, 1.88777e6, 900940.0, 210733.0, 12237.0, 49.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
e20 = [2.75013e6, 2.12614e6, 1.32929e6, 575468.0, 137368.0, 13120.0, 272.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
e30 = [2.75013e6, 2.36452e6, 1.90067e6, 1.45761e6, 1.1215e6, 872924.0, 751132.0, 701637.0, 683643.0, 677102.0, 674651.0, 673708.0, 673341.0, 673196.0, 673138.0, 673115.0, 673106.0, 673102.0, 673101.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0, 673100.0]
e40 = [2.75013e6, 2.6029e6, 2.54134e6, 2.43814e6, 2.33911e6, 2.21278e6, 2.11645e6, 2.04741e6, 1.9975e6, 1.95875e6, 1.92543e6, 1.89382e6, 1.86146e6, 1.82676e6, 1.78882e6, 1.74743e6, 1.7031e6, 1.65705e6, 1.61114e6, 1.56749e6, 1.52807e6, 1.49422e6, 1.46649e6, 1.44468e6, 1.42809e6, 1.41579e6, 1.40685e6, 1.40044e6, 1.39589e6, 1.39267e6]
e50 = [2.75013e6, 2.84127e6, 3.10028e6, 3.31414e6, 3.52637e6, 3.56799e6, 3.6204e6, 3.6988e6, 3.82215e6, 4.03019e6, 4.25022e6, 4.23891e6, 4.22731e6, 4.2159e6, 4.20469e6, 4.19427e6, 4.18496e6, 4.17695e6, 4.17028e6, 4.16487e6, 4.16061e6, 4.15731e6, 4.15479e6, 4.1529e6, 4.15149e6, 4.15044e6, 4.14967e6, 4.14911e6, 4.1487e6, 4.1484e6]
plot(e,xlabel="t",ylabel="Total employment",label="basic",lw=2,leg=:outertopright)
plot!(e2,lw=2,label="1x")
plot!(e10,lw=2,label="10x")
plot!(e20,lw=2,label="20x")
plot!(e30,lw=2,label="30x")
plot!(e40,lw=2,label="40x")
plot!(e50,lw=2,label="50x")

# time
T = 30

# parameter array
# add column vector for time
p = Array{Float64}(undef,T,no_sectors,3)
for i = 1:T
    #p[i,no_sectors+1] = i
    for j = 1:no_sectors
        p[i,j,1] = 0.0
        # no perturbation except when t=2
        if i == 2
            p[i,j,1] = (employed[j,:Mar] - employed[j,:Feb])/(employed[j,:Feb]*1)
        end
        p[i,j,2] = 0.0
        p[i,j,3] = 0.0
    end
end

# perturbation
D = Array{Float64}(undef,T,no_sectors)
for i = 1:T
    for j = 1:no_sectors
        D[i,j] = p[i,j,1]+p[i,j,2]+p[i,j,3]
    end
end
#print(D)

# employment
Ep = Array{Float64}(undef,T,no_sectors+1)
Up = Array{Float64}(undef,T,no_sectors+1)
# initial conditions
for i = 1:no_sectors
    Ep[1,1] = 1.0
    Ep[1,i+1] = employed[i,:Mar]
    Up[1,1] = 1.0
    Up[1,i+1] = 0.0
end

# simulate
for i = 2:T
    Ep[i,1] = convert(Float64,i)
    for j = 1:no_sectors
        alpha = A[j,j]*(1.0+D[i,j])*Ep[i-1,j+1]/Ep[1,j+1]
        #println(alpha)
        beta = 0.0
        for k = 1:no_sectors
            beta = beta + ((1.0+D[i,k])*(B[j,k]+C[j,k])*(Ep[i-1,k+1]/Ep[1,k+1]))
        end
        #println(beta)
        a = alpha+beta
        #println(a)
        # modify E and U
        if a-1.0 >= 0 # positive growth
            del_E = round(a*(Ep[i-1,j+1]) - Ep[i-1,j+1])
            #println(del_E)
            if del_E <= Up[i-1,j+1] # if re-hiring possible
                Ep[i,j+1] = round(a*Ep[i-1,j+1]) #+ del_E
                Up[i,j+1] = round((Up[i-1,j+1]*(1-p[2])) + ((Ep[i-1,j+1]-Ep[i,j+1])))*(1-p[2])
            elseif del_E > Up[i-1,j+1]
                Ep[i,j+1] = Ep[i-1,j+1] + Up[i-1,j+1]
                Up[i,j+1] = 0.0
            end
        elseif a-1.0 < 0 # negative growth
            del_E = Ep[i-1,j+1] - round(a*(Ep[i-1,j+1]))
            Ep[i,j+1] = round(a*(Ep[i-1,j+1]))
            Up[i,j+1] = Up[i-1,j+1]*(1-p[2]) + (Ep[i-1,j+1]-Ep[i,j+1])
        end
        # no negative unemployment
        if Up[i,j+1] < 0.0
            Up[i,j+1] = 0.0
        end
        if Up[i,j+1] >= Ep[1,j+1]
            Up[i,j+1] = Ep[1,j+1]
        end
    end
end
#print(E)

# plot
ep = Float64[]
up = Float64[]
for i = 1:T
    push!(ep,sum(Ep[i,:])-Ep[i,1])
    push!(up,sum(Up[i,:])-Up[i,1])
end
plot(ep,xlabel="t",ylabel="Total employment",label="pulse model",lw=2)
plot!(e,label="basic press model",lw=2)

#println("\nAbout to print ep")
#println(ep)
#println("\nAbout to print e")
#println(e)


