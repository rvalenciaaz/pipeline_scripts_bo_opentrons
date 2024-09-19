# defining bounds
bounds = torch.stack([torch.zeros(dim), torch.ones(dim)])
if args.method == "sobol":
    samples = draw_sobol_samples(bounds=bounds, n=init_samples, q=1).reshape(init_samples, dim)
else:  # LHS method
    samples = torch.tensor(pyDOE2.lhs(n=dim, samples=init_samples))

#extract labels of components
labels_df = pd.read_csv(col_labels)
col_labels_list = labels_df["Component"].to_list()

#save initial sample table with components as columns
init_table = pd.DataFrame({"sample": [f"{iteration}_{i+1}" for i in range(init_samples)]})
init_table[col_labels_list] = samples
init_table.to_csv(f"samples/{iteration}_samples.csv", index=False)
