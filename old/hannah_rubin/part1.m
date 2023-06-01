% citation gaps part 1, basic model

reps = 100; % # times new networks created
A = 100; % # simulations on each network
C = 200; % citation chances per simulation
P = 100; % nodes in network
p1 = .5:.1:.9; % proportion majority group members
H = .5:.1:.9; % determines in- vs. out-group linking probability
cit = .3; %probability of citing 

% track: M cites M, Mm, mM, mm (M=majority, m=minority)
gc = zeros(4,length(p1),length(H),A,reps); 


for pr1=p1
    for h=H
        for r=1:reps    
            % make a multitype random graph
            pin=h/10; pout=(1-h)/10; run('multitype.m')
            
            for a = 1:A
                % pick authors (one from maj. and one from min.)
                onez=find(types(1,1:N)==1); zeroz=find(types(1,1:N)==0);
                disc(1,1)=randsample(onez,1); disc(1,2)=randsample(zeroz,1);

                % draw people from the network at random to cite the papers
                citers = randsample(1:N,C,true); G=graph(net); 
                
                % and record who cites whom
                gcita=zeros(1,4); % M cites M, Mm, mM, mm (M=majority, m=minority)
                for c=citers
                    d = distances(G,c,disc); %  path length to authors
                    if min(d)==0 % self-citation always happens
                        if c==disc(1,1)
                            gcita(1,1)=gcita(1,1)+1; %MM
                        else
                            gcita(1,4)=gcita(1,4)+1; %mm
                        end
                    else % otherwise, depends on path length & citation prob.
                        pc1= cit^d(1);
                        pc2= cit^d(2); 
                        if rand() < pc1
                            if types(1,c)==1
                                gcita(1,1)=gcita(1,1)+1; %MM
                            else
                                gcita(1,3)=gcita(1,3)+1; %mM
                            end
                        end
                        if rand() < pc2
                            if types(1,c)==1
                                gcita(1,2)=gcita(1,2)+1; %Mm
                            else
                                gcita(1,4)=gcita(1,4)+1; %mm
                            end
                        end
                    end
                end
                % record final counts for that simulation
                gc(:,find(p1==pr1),find(H==h),a,r)=gcita'; % MM, Mm, mM, mm
            end
        end
    end
    datestr(clock) % (track progress to see how long it's taking)
end


% get data from gc into form for the graphs
cites=zeros(2,length(p1),length(H)); % overall citations for M and m
gcites=zeros(4,length(p1),length(H)); grel=gcites;
citesR=zeros(length(p1),length(H)); citesgap=citesR; citesM=citesR; citesm=citesR;
for pr1=p1
    for h=H
        maj=find(p1==pr1); hom=find(H==h);
        for i=1:4
            gcites(i,maj,hom)=sum(sum(gc(i,maj,hom,:,:)))/(A*reps); 
        end
        for i=1:2
            grel(i,maj,hom)=gcites(i,maj,hom)/pr1;
        end
        for i =3:4
            grel(i,maj,hom)=gcites(i,maj,hom)/(1-pr1);
        end
        cites(1,maj,hom)=(gcites(1,maj,hom)+gcites(3,maj,hom)); % total M
        cites(2,maj,hom)=(gcites(2,maj,hom)+gcites(4,maj,hom)); % total m
        citesR(maj,hom)=cites(1,maj,hom)/cites(2,maj,hom); % overall citations for M vs. m (alternate measure of gap)
        citesgap(maj,hom)=(cites(1,maj,hom)-cites(2,maj,hom))/(cites(1,maj,hom)+cites(2,maj,hom)); % gap
        citesM(maj,hom)=grel(1,maj,hom)/grel(2,maj,hom); %M citing M / M citing m
        citesm(maj,hom)=grel(3,maj,hom)/grel(4,maj,hom); %m citing M / m citing m
    end
end


legendCell = cellstr(num2str((H')/10, 'P(in)=%-.2f'));
clear set

figure('rend','painters','pos',[800 100 250 250])
x=p1;
plot(x,reshape(citesM, [length(p1),length(H)]))
ylabel('ratio in majority')
xlabel('majority size')
%legend(legendCell, 'Location', 'Best')

figure('rend','painters','pos',[535 100 250 250])
x=p1;
plot(x,reshape(citesm, [length(p1),length(H)]))
ylabel('ratio in minority')
xlabel('majority size')
%legend(legendCell, 'Location', 'Best')

% figure('rend','painters','pos',[100 100 250 300])
% x=p1;
% plot(x,reshape(citesR, [length(p1),length(H)]))
% ylabel('majority to minority citation ratio')
% xlabel('majority size')
% legend(legendCell, 'Location', 'Best', 'FontSize', 8)

figure('rend','painters','pos',[125 100 400 300]) %400 300
x=p1;
plot(x,reshape(citesgap, [length(p1),length(H)]))
ylabel('citation gap')
xlabel('majority size')
ylim([-.05 .4])
%legend(legendCell, 'Location', 'Best', 'FontSize', 8)
