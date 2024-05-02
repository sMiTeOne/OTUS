box.cfg{listen = 3301}

users = box.schema.space.create('users', {
    if_not_exists = true
})

box.space.users:format({
    { 'uid', type = 'string' },
    { 'score', type = 'number' }
})

box.space.users:create_index('uid', {
    type = 'hash', parts = {'uid'}
})


users = box.schema.space.create('clients', {
    if_not_exists = true
})

box.space.clients:format({
    { 'cid', type = 'string' },
    { 'interests', type = 'array' }
})

box.space.clients:create_index('cid', {
    type = 'hash', parts = {'cid'}
})
