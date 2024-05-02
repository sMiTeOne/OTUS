box.cfg{listen = 3301}

users = box.schema.space.create('users', {
    if_not_exists = true
})

box.space.users:format({
    { 'uid', type = 'string' },
    { 'score', type = 'number' }
})

box.space.users:create_index('primary', {
    type = 'hash', parts = {'uid'}
})
